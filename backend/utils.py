# =============================================================================
#                        Project Oasis - Utils
#
# This file holds helper functions, the "black box" geospatial calculation,
# and the main service function for recalculating areas.
# =============================================================================

import numpy as np
import matplotlib.patches as patches
from matplotlib.path import Path
from scipy.spatial.distance import cdist
from tqdm import tqdm
from skimage.measure import find_contours, approximate_polygon
from pyproj import Transformer
from geoalchemy2.shape import to_shape
from shapely.geometry import shape
from flask import current_app

# Import our database models
from models import Area, Well, db

# --- --- --- --- --- --- --- --- --- ---
# --- DATABASE <-> BLACK BOX HELPERS ---
# --- --- --- --- --- --- --- --- --- ---

def _geometry_to_lonlat(geom):
    """Converts a GeoAlchemy Geometry object (Point) to a (lon, lat) tuple."""
    # Use raw SQL to extract coordinates from PostGIS binary data
    from sqlalchemy import text
    from models import db
    
    # Get the well ID from the geom object (assuming it's a Well instance)
    if hasattr(geom, 'id'):
        well_id = geom.id
        query = text("SELECT ST_X(location) as lng, ST_Y(location) as lat FROM wells WHERE id = :well_id")
        result = db.session.execute(query, {"well_id": well_id}).fetchone()
        if result:
            return (float(result.lng), float(result.lat))
    
    # Fallback: try to use to_shape if it's a proper geometry object
    try:
        shapely_geom = to_shape(geom)
        mapping = shapely_geom.__geo_interface__
        coords = mapping['coordinates']
        return (coords[0], coords[1]) # (lon, lat)
    except:
        raise ValueError("Could not extract coordinates from geometry")

def _geometry_to_lonlat_list(geom):
    """Converts a GeoAlchemy Geometry object (Polygon) to a list of (lon, lat) tuples."""
    # Use raw SQL to extract coordinates from PostGIS binary data
    from sqlalchemy import text
    from models import db
    
    # Get the area ID from the geom object (assuming it's an Area instance)
    if hasattr(geom, 'id'):
        area_id = geom.id
        query = text("SELECT ST_AsText(boundary) as boundary_text FROM areas WHERE id = :area_id")
        result = db.session.execute(query, {"area_id": area_id}).fetchone()
        if result and result.boundary_text:
            # Parse the WKT POLYGON string
            import re
            polygon_match = re.search(r'POLYGON\(\(([^)]+)\)\)', result.boundary_text)
            if polygon_match:
                coords_str = polygon_match.group(1)
                coord_pairs = coords_str.split(',')
                coords = []
                for pair in coord_pairs:
                    parts = pair.strip().split()
                    if len(parts) >= 2:
                        lng = float(parts[0])
                        lat = float(parts[1])
                        coords.append((lng, lat))
                return coords
    
    # Fallback: try to use to_shape if it's a proper geometry object
    try:
        shapely_geom = to_shape(geom)
        mapping = shapely_geom.__geo_interface__
        coords = mapping['coordinates'][0] 
        return [(lon, lat) for lon, lat in coords]
    except:
        raise ValueError("Could not extract coordinates from geometry")

def _lonlat_list_to_geometry(lonlat_list):
    """Converts a list of (lon, lat) tuples back to a DB-saveable WKT string."""
    # Convert numpy arrays to lists if needed
    if hasattr(lonlat_list[0], 'tolist'):
        lonlat_list = [point.tolist() if hasattr(point, 'tolist') else point for point in lonlat_list]
    
    # Ensure the polygon is closed (first and last points are the same)
    if len(lonlat_list) > 0 and lonlat_list[0] != lonlat_list[-1]:
        lonlat_list.append(lonlat_list[0])
    
    wkt_coords = ", ".join(f"{lon} {lat}" for lon, lat in lonlat_list)
    return f"SRID=4326;POLYGON(({wkt_coords}))"

# --- --- --- --- --- --- --- --- --- ---
# --- BLACK BOX FUNCTION & HELPERS ---
# (Your _compute_weighted_areas, _get_vector_boundaries, 
# and calculate_weighted_polygons functions go here)
# ...
# (Pasting your code here for completeness)
# ...
def _compute_weighted_areas(points_xy, target_weights, boundary_xy, 
                           resolution, max_iterations, tolerance, 
                           damping_factor, verbose):
    n_points = len(points_xy)
    min_coords = np.min(boundary_xy, axis=0)
    max_coords = np.max(boundary_xy, axis=0)
    padding = (max_coords - min_coords) * 0.05
    x = np.linspace(min_coords[0] - padding[0], max_coords[0] + padding[0], resolution)
    y = np.linspace(min_coords[1] - padding[1], max_coords[1] + padding[1], resolution)
    grid_x_coords, grid_y_coords = x, y 
    xx, yy = np.meshgrid(x, y)
    grid_coords = np.vstack([xx.ravel(), yy.ravel()]).T
    boundary_path = Path(boundary_xy)
    mask = boundary_path.contains_points(grid_coords)
    grid_coords_inside = grid_coords[mask]
    n_pixels_inside = len(grid_coords_inside)
    if n_pixels_inside == 0:
        raise ValueError("Bounding shape has no area or grid is too coarse.")
    target_weights_safe = np.maximum(target_weights, 0)
    total_weight = np.sum(target_weights_safe)
    if total_weight == 0:
        if verbose: print("Warning: All target weights are zero.")
        assignment_grid = np.full((resolution, resolution), -1.0)
        return assignment_grid, (grid_x_coords, grid_y_coords)
    target_proportions = target_weights_safe / total_weight
    target_pixel_counts = target_proportions * n_pixels_inside
    current_weights = np.ones(n_points)
    current_weights[target_weights <= 0] = 1e-9 
    if verbose: print(f"Starting iterations... Target pixels: {n_pixels_inside}")
    iterator = range(max_iterations)
    if verbose:
        iterator = tqdm(range(max_iterations), desc="Optimizing Areas")
    for i in iterator:
        dists = cdist(points_xy, grid_coords_inside)
        weighted_dists = dists / current_weights[:, np.newaxis]
        assignments = np.argmin(weighted_dists, axis=0)
        actual_pixel_counts = np.bincount(assignments, minlength=n_points)
        proportional_error = (actual_pixel_counts - target_pixel_counts) / n_pixels_inside
        max_error = np.max(np.abs(proportional_error))
        if max_error < tolerance:
            if verbose: print(f"\nConvergence reached in {i+1} iterations.")
            break
        actual_safe = np.maximum(actual_pixel_counts, 1.0)
        correction_factor = (target_pixel_counts / actual_safe)
        current_weights *= (correction_factor ** damping_factor)
        current_weights[target_weights <= 0] = 1e-9
    if i == max_iterations - 1 and verbose:
        print(f"\nMax iterations reached. Max proportional error: {max_error:.4f}")
    assignment_grid = np.full((resolution, resolution), -1.0)
    mask_2d = mask.reshape(resolution, resolution)
    assignment_grid[mask_2d] = assignments
    return assignment_grid, (grid_x_coords, grid_y_coords)

def _get_vector_boundaries(grid, grid_x_coords, grid_y_coords, n_points, 
                          simplification_tolerance, verbose):
    vector_boundaries = {}
    stats = {} 
    if verbose: print(f"\nVectorizing boundaries (Tolerance={simplification_tolerance}px)...")
    for i in range(n_points):
        region_mask = (grid == i).astype(np.float64)
        contours_raw = find_contours(region_mask, level=0.5)
        region_segments = []
        total_points_before = 0
        total_points_after = 0
        for contour in contours_raw:
            total_points_before += len(contour)
            if simplification_tolerance > 0:
                contour_simplified = approximate_polygon(contour, 
                                                    tolerance=simplification_tolerance)
            else:
                contour_simplified = contour
            total_points_after += len(contour_simplified)
            x_interpolated = np.interp(contour_simplified[:, 1], 
                                       np.arange(len(grid_x_coords)), 
                                       grid_x_coords)
            y_interpolated = np.interp(contour_simplified[:, 0], 
                                       np.arange(len(grid_y_coords)), 
                                       grid_y_coords)
            region_segments.append(np.column_stack([x_interpolated, y_interpolated]))
        vector_boundaries[i] = region_segments
        stats[i] = (total_points_before, total_points_after)
    if verbose:
        for i in range(n_points):
            before, after = stats[i]
            if before > 0:
                print(f"  - Region {i} ({stats.get(i, 'N/A')}): {before} points -> {after} points")
    return vector_boundaries

def calculate_weighted_polygons(
    point_ids: list, 
    points_lon_lat: list,
    point_weights: list, 
    boundary_lon_lat: list, 
    resolution: int = 300, 
    max_iterations: int = 100, 
    tolerance: float = 0.005, 
    damping_factor: float = 0.2, 
    simplification_tolerance: float = 2.0,
    verbose: bool = True
) -> dict:
    if not (len(point_ids) == len(points_lon_lat) == len(point_weights)):
        raise ValueError("Input lists (point_ids, points_lon_lat, point_weights) must all have the same length.")
    n_points = len(point_ids)
    CRS_LONLAT = "EPSG:4326"
    CRS_XY = "ESRI:54034"
    transformer_to_xy = Transformer.from_crs(CRS_LONLAT, CRS_XY, always_xy=True)
    transformer_to_lonlat = Transformer.from_crs(CRS_XY, CRS_LONLAT, always_xy=True)
    if verbose: print("Projecting coordinates to equal-area grid...")
    boundary_xy = np.array(list(transformer_to_xy.itransform(boundary_lon_lat)))
    points_xy = np.array(list(transformer_to_xy.itransform(points_lon_lat)))
    grid, (grid_x, grid_y) = _compute_weighted_areas(
        points_xy, 
        np.array(point_weights), 
        boundary_xy,
        resolution, 
        max_iterations,
        tolerance, 
        damping_factor, 
        verbose
    )
    vector_boundaries_xy = _get_vector_boundaries(
        grid, 
        grid_x, 
        grid_y, 
        n_points, 
        simplification_tolerance, 
        verbose
    )
    if verbose: print("\nProjecting vector boundaries back to (lon, lat)...")
    output_polygons = {}
    for i, point_id in enumerate(point_ids):
        xy_segments = vector_boundaries_xy[i]
        lonlat_segments = []
        for segment_xy in xy_segments:
            segment_lonlat = np.array(list(transformer_to_lonlat.itransform(segment_xy)))
            lonlat_segments.append(segment_lonlat)
        output_polygons[i] = lonlat_segments
    if verbose: print("Calculation complete.")
    return output_polygons

# --- --- --- --- --- --- --- --- --- --- ---
# --- --- --- NEW SERVICE FUNCTION --- ---
# --- --- --- --- --- --- --- --- --- --- ---

def recalculate_service_areas(area_id):
    """
    Service function to recalculate and save service areas for all active
    wells in a given area. This is the core logic, callable from any endpoint.
    """
    try:
        area = Area.query.get(area_id)
        if not area:
            raise ValueError(f"Area with id {area_id} not found.")

        # Get all wells that should be part of the calculation
        wells_in_area = Well.query.filter(
            Well.area_id == area_id,
            Well.status.in_(['completed', 'building'])
        ).all()
        
        # Also grab broken wells, they participate but with 0 weight
        broken_wells_in_area = Well.query.filter(
            Well.area_id == area_id,
            Well.status == 'broken'
        ).all()
        
        all_wells_to_calculate = wells_in_area + broken_wells_in_area

        if len(all_wells_to_calculate) == 0:
            current_app.logger.info(f"No active or broken wells in area {area_id} to calculate.")
            return [] # Nothing to do

        # --- Format data for the black box ---
        point_ids = [str(well.id) for well in all_wells_to_calculate]
        points_lon_lat = [_geometry_to_lonlat(well) for well in all_wells_to_calculate]
        # Use capacity as weight. Broken wells have 0 capacity.
        point_weights = [well.capacity if well.status != 'broken' else 0 for well in all_wells_to_calculate]
        boundary_lon_lat = _geometry_to_lonlat_list(area)
        
        current_app.logger.info(f"Recalculating for {len(point_ids)} wells in area {area.name}...")

        # --- Run the Black Box ---
        polygon_map = calculate_weighted_polygons(
            point_ids=point_ids,
            points_lon_lat=points_lon_lat,
            point_weights=point_weights,
            boundary_lon_lat=boundary_lon_lat,
            resolution=200,
            simplification_tolerance=1.5,
            verbose=False 
        )
        
        # --- Save results back to the database ---
        for i, well in enumerate(all_wells_to_calculate):
            # Use the index 'i' as the key from the black box
            if i in polygon_map and polygon_map[i]:
                # The black box returns a list of polygons, we take the first one
                polygon_lonlat_list = polygon_map[i][0]
                well.service_area = _lonlat_list_to_geometry(polygon_lonlat_list)
            else:
                # If black box fails for one, nullify its area
                well.service_area = None
        
        db.session.commit()
        current_app.logger.info(f"Recalculation for area {area_id} and save complete.")
        return all_wells_to_calculate

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in recalculation service: {e}", exc_info=True)
        # Re-raise the exception so the endpoint can handle the HTTP response
        raise e