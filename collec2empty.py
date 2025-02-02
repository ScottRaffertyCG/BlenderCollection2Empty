import bpy

def process_objects_in_collection(collection, empty):
    """
    Process all objects in a collection and its children.
    Args:
        collection: The collection containing objects
        empty: The empty object to parent to
    """
    # Create a list of objects to process to avoid modification during iteration
    objects_to_process = list(collection.objects)
    
    # Process direct objects in this collection
    for obj in objects_to_process:
        try:
            # Unlink from current collection
            collection.objects.unlink(obj)
            
            # Link to scene collection if not already there
            if obj.name not in bpy.context.scene.collection.objects:
                bpy.context.scene.collection.objects.link(obj)
            
            # Only set parent if object doesn't already have one
            if obj.parent is None:
                obj.parent = empty
        except RuntimeError as e:
            print(f"Warning: Could not process object {obj.name}: {str(e)}")

def create_empty_from_collection(collection, parent_empty=None):
    """
    Create an Empty object from a collection and maintain hierarchy.
    Args:
        collection: The collection to convert
        parent_empty: The parent Empty object (if any)
    Returns:
        The created Empty object
    """
    try:
        # Create new empty
        empty = bpy.data.objects.new(collection.name, None)
        empty.empty_display_type = 'PLAIN_AXES'
        
        # Link empty to scene collection
        bpy.context.scene.collection.objects.link(empty)
        
        # Set parent if exists
        if parent_empty:
            empty.parent = parent_empty
        
        # Process objects in this collection
        process_objects_in_collection(collection, empty)
        
        # Create a list of child collections to avoid modification during iteration
        child_collections = list(collection.children)
        
        # Process child collections recursively
        for child_collection in child_collections:
            child_empty = create_empty_from_collection(child_collection, empty)
            # Process objects in child collection
            process_objects_in_collection(child_collection, child_empty)
        
        return empty
    except Exception as e:
        print(f"Error processing collection {collection.name}: {str(e)}")
        return None

def is_top_level_collection(collection):
    """
    Check if a collection is top-level (not a child of any other collection).
    """
    scene_collection = bpy.context.scene.collection
    for other_col in bpy.data.collections:
        if other_col != scene_collection and other_col != collection:
            if collection.name in [c.name for c in other_col.children]:
                return False
    return True

def find_top_level_collections():
    """
    Find all top-level collections (excluding Scene Collection).
    Returns:
        List of top-level collections
    """
    scene_collection = bpy.context.scene.collection
    return [col for col in bpy.data.collections 
            if col != scene_collection and is_top_level_collection(col)]

def convert_collections_to_empties():
    """
    Convert all collections to Empty objects while preserving hierarchy.
    """
    # Get top-level collections
    top_level_collections = find_top_level_collections()
    
    # Process each top-level collection
    for collection in top_level_collections:
        create_empty_from_collection(collection)

def cleanup_collections():
    """
    Remove all collections except Scene Collection.
    """
    for collection in bpy.data.collections:
        if collection != bpy.context.scene.collection:
            try:
                bpy.data.collections.remove(collection)
            except Exception as e:
                print(f"Warning: Could not remove collection {collection.name}: {str(e)}")

def main():
    # Convert collections to empties
    convert_collections_to_empties()
    # Clean up empty collections
    cleanup_collections()

if __name__ == "__main__":
    main()
