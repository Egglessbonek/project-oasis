# =============================================================================
#                        Project Oasis - Utils
#
# This file holds helper functions, the "black box" geospatial calculation,
# and the main service functions for recalculating areas and updating weights.
# =============================================================================

import numpy as np
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
    shapely_geom = to_shape(geom)
    mapping = shapely_geom.__geo_interface__
    coords = mapping['coordinates']
    return (coords[0], coords[1]) # (lon, lat)

def _geometry_to_lonlat_list(geom):
    """Converts a GeoAlchemy Geometry object (Polygon) to a list of (lon, lat) tuples."""
    shapely_geom = to_shape(geom)
    mapping = shapely_geom.__geo_interface__
    # This handles both Polygons and MultiPolygons by taking the exterior of the first ring
    coords = mapping['coordinates'][0] 
    return [(lon, lat) for lon, lat in coords]

def _lonlat_list_to_geometry(lonlat_list):
    """Converts a list of (lon, lat) tuples back to a DB-saveable WKT string."""
    lonlat_list = list(map(tuple, lonlat_list))  # ensure it's a list of tuples

    # Ensure the polygon is closed (first and last points are the same)
    if not lonlat_list or lonlat_list[0] != lonlat_list[-1]:
        lonlat_list.append(lonlat_list[0])
    
    wkt_coords = ", ".join(f"{lon} {lat}" for lon, lat in lonlat_list)
    return f"SRID=4326;POLYGON(({wkt_coords}))"


# --- --- --- --- --- --- --- --- --- ---
# --- BLACK BOX FUNCTION & HELPERS ---
# --- --- --- --- --- --- --- --- --- ---
def _compute_weighted_areas(points_xy, target_weights, boundary_xy, 
                           resolution, max_iterations, tolerance, 
                           damping_factor, verbose):
    """
    (Internal Helper Function)
    Computes the iterative pixel-based Voronoi diagram on a 2D plane.
    """
    
    n_points = len(points_xy)
    
    # --- 1. Create Grid and Bounding Shape Mask ---
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

    # --- 2. Calculate Target Areas (as pixel counts) ---
    target_weights_safe = np.maximum(target_weights, 0)
    total_weight = np.sum(target_weights_safe)

    if total_weight == 0:
        if verbose: print("Warning: All target weights are zero.")
        assignment_grid = np.full((resolution, resolution), -1.0)
        return assignment_grid, (grid_x_coords, grid_y_coords)

    target_proportions = target_weights_safe / total_weight
    target_pixel_counts = target_proportions * n_pixels_inside

    # --- 3. Iteration Loop ---
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

    # --- 4. Create Final Output Grid ---
    assignment_grid = np.full((resolution, resolution), -1.0)
    mask_2d = mask.reshape(resolution, resolution)
    assignment_grid[mask_2d] = assignments
    
    return assignment_grid, (grid_x_coords, grid_y_coords)

def _get_vector_boundaries(grid, grid_x_coords, grid_y_coords, n_points, 
                          simplification_tolerance, verbose):
    """
    (Internal Helper Function)
    Extracts simplified vector boundary lines from the raster grid for each region.
    """
    vector_boundaries = {}
    stats = {} 
    
    if verbose: print(f"\nVectorizing boundaries (Tolerance={simplification_tolerance}px)...")
    
    for i in range(n_points):
        region_mask = (grid == i).astype(np.float64)
        contours_raw = find_contours(region_mask, level=0.5)
        
        region_segments = []
        for contour in contours_raw:
            if simplification_tolerance > 0:
                contour_simplified = approximate_polygon(contour, 
                                                    tolerance=simplification_tolerance)
            else:
                contour_simplified = contour
            
            x_interpolated = np.interp(contour_simplified[:, 1], 
                                       np.arange(len(grid_x_coords)), 
                                       grid_x_coords)
            y_interpolated = np.interp(contour_simplified[:, 0], 
                                       np.arange(len(grid_y_coords)), 
                                       grid_y_coords)

            region_segments.append(np.column_stack([x_interpolated, y_interpolated]))
            
        vector_boundaries[i] = region_segments
        
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
    print(point_ids)
    print(points_lon_lat)
    print(point_weights)
    if not (len(point_ids) == len(points_lon_lat) == len(point_weights)):
        raise ValueError("Input lists (point_ids, points_lon_lat, point_weights) must all have the same length.")
    
    n_points = len(point_ids)
    
    CRS_LONLAT = "EPSG:4326"
    CRS_XY = "ESRI:54034" # World Cylindrical Equal Area
    
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
        xy_segments = vector_boundaries_xy.get(i, [])
        
        lonlat_segments = []
        for segment_xy in xy_segments:
            segment_lonlat = np.array(list(transformer_to_lonlat.itransform(segment_xy)))
            lonlat_segments.append(segment_lonlat)
            
        output_polygons[point_id] = lonlat_segments
    
    if verbose: print("Calculation complete.")
    return output_polygons


# --- --- --- --- --- --- --- --- --- --- ---
# --- --- --- SERVICE FUNCTIONS --- ---
# --- --- --- --- --- --- --- --- --- --- ---

def update_area_weights(area_id):
    """
    Updates the operational 'weight' of all wells in an area based on
    their current load vs. capacity.
    """
    wells_in_area = Well.query.filter(Well.area_id == area_id).all()
    
    if not wells_in_area:
        current_app.logger.info(f"No wells in area {area_id} to update weights for.")
        return

    current_app.logger.info(f"Updating weights for {len(wells_in_area)} wells in area {area_id}...")

    for well in wells_in_area:
        if well.status == 'broken':
            well.weight = 0
            continue

        if well.capacity == 0:
            well.weight = 0
            continue
            
        load_ratio = well.current_load / well.capacity
        
        if load_ratio >= 1.2: # 120% full or more
            well.weight = max(0, int(well.weight * 0.8)) # Decrease weight by 20%
        elif load_ratio >= 0.8: # 80% full or more
            well.weight = int(well.weight * 1.25) # Increase weight by 25%
            
    db.session.commit()
    current_app.logger.info(f"Weight update complete for area {area_id}.")


def recalculate_service_areas(area_id):
    """
    Service function to recalculate and save service areas for all wells
    in a given area, using their current 'weight' from the database.
    """
    try:
        area = Area.query.get(area_id)
        if not area:
            raise ValueError(f"Area with id {area_id} not found.")

        all_wells_to_calculate = Well.query.filter(Well.area_id == area_id).all()

        if len(all_wells_to_calculate) == 0:
            current_app.logger.info(f"No wells in area {area_id} to calculate.")
            return []

        # Ensure completed wells with weight=0 get weight=capacity
        for well in all_wells_to_calculate:
            if well.status == 'completed' and well.weight == 0:
                well.weight = well.capacity
            else:
                well.weight = 0
        db.session.commit()

        # --- Format data for the black box ---
        point_ids = [str(well.id) for well in all_wells_to_calculate]
        points_lon_lat = [_geometry_to_lonlat(well.location) for well in all_wells_to_calculate]
        point_weights = [well.weight for well in all_wells_to_calculate]
        boundary_lon_lat = _geometry_to_lonlat_list(area.boundary)
        
        current_app.logger.info(f"Recalculating for {len(point_ids)} wells in area {area.name} with weights: {point_weights}")

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
        for well in all_wells_to_calculate:
            well_id_str = str(well.id)
            if well_id_str in polygon_map and polygon_map[well_id_str]:
                polygon_lonlat_list = polygon_map[well_id_str][0]
                well.service_area = _lonlat_list_to_geometry(polygon_lonlat_list)
            else:
                well.service_area = None
        
        db.session.commit()
        current_app.logger.info(f"Recalulation for area {area_id} and save complete.")
        return all_wells_to_calculate

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in recalculation service: {e}", exc_info=True)
        raise e
