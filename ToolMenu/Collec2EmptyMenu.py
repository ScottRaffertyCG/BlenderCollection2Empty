bl_info = {
    "name": "Collection to Empty Actor Converter",
    "author": "Scott Rafferty",
    "version": (0, 1),
    "blender": (4, 3, 0),
    "location": "3D Viewport > Sidebar > Tool > Collection Convert",
    "description": "Converts collections to empty objects while preserving hierarchy",
    "category": "Object",
}

import bpy
from bpy.types import Operator, Panel

class CONVERT_OT_collections_to_empties(Operator):
    bl_idname = "object.convert_collections_to_empties"
    bl_label = "Convert Collections to Empties"
    bl_description = "Convert all collections to empty objects while preserving hierarchy"
    bl_options = {'REGISTER', 'UNDO'}

    def process_objects_in_collection(self, collection, empty):
        objects_to_process = list(collection.objects)
        
        for obj in objects_to_process:
            try:
                collection.objects.unlink(obj)
                
                if obj.name not in bpy.context.scene.collection.objects:
                    bpy.context.scene.collection.objects.link(obj)
                
                if obj.parent is None:
                    obj.parent = empty
            except RuntimeError as e:
                self.report({'WARNING'}, f"Could not process object {obj.name}: {str(e)}")

    def create_empty_from_collection(self, collection, parent_empty=None):
        try:
            empty = bpy.data.objects.new(collection.name, None)
            empty.empty_display_type = 'PLAIN_AXES'
            
            bpy.context.scene.collection.objects.link(empty)
            
            if parent_empty:
                empty.parent = parent_empty
            
            self.process_objects_in_collection(collection, empty)
            
            child_collections = list(collection.children)
            
            for child_collection in child_collections:
                child_empty = self.create_empty_from_collection(child_collection, empty)
                self.process_objects_in_collection(child_collection, child_empty)
            
            return empty
        except Exception as e:
            self.report({'ERROR'}, f"Error processing collection {collection.name}: {str(e)}")
            return None

    def is_top_level_collection(self, collection):
        scene_collection = bpy.context.scene.collection
        for other_col in bpy.data.collections:
            if other_col != scene_collection and other_col != collection:
                if collection.name in [c.name for c in other_col.children]:
                    return False
        return True

    def find_top_level_collections(self):
        scene_collection = bpy.context.scene.collection
        return [col for col in bpy.data.collections 
                if col != scene_collection and self.is_top_level_collection(col)]

    def cleanup_collections(self):
        for collection in bpy.data.collections:
            if collection != bpy.context.scene.collection:
                try:
                    bpy.data.collections.remove(collection)
                except Exception as e:
                    self.report({'WARNING'}, f"Could not remove collection {collection.name}: {str(e)}")

    def execute(self, context):
        try:
            # Get top-level collections
            top_level_collections = self.find_top_level_collections()
            
            # Process each top-level collection
            for collection in top_level_collections:
                self.create_empty_from_collection(collection)
            
            # Cleanup collections
            self.cleanup_collections()
            
            self.report({'INFO'}, "Successfully converted collections to empties")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error during conversion: {str(e)}")
            return {'CANCELLED'}

class VIEW3D_PT_collection_converter_panel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'  # This puts it in the sidebar
    bl_label = "Collection Convert"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        # Add conversion button
        row = layout.row()
        row.operator(CONVERT_OT_collections_to_empties.bl_idname, 
                    text="Convert Collections", 
                    icon='OUTLINER_OB_EMPTY')
        
        # Add information about the tool
        box = layout.box()
        col = box.column()
        col.label(text="This tool will:", icon='INFO')
        col.label(text="• Convert collections to empties")
        col.label(text="• Preserve hierarchy")
        col.label(text="• Maintain parent relationships")

# Add to the Object menu
def menu_func(self, context):
    self.layout.operator(CONVERT_OT_collections_to_empties.bl_idname)

classes = (
    CONVERT_OT_collections_to_empties,
    VIEW3D_PT_collection_converter_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    # Add to the Object menu
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    # Remove from the Object menu
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
