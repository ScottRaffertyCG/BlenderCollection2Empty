bl_info = {
    "name": "Empty to Collection Organizer",
    "author": "Scott Rafferty",
    "version": (1, 0),
    "blender": (4, 3, 0),
    "location": "3D Viewport > Sidebar > Tool > Empty Convert",
    "description": "Creates collections for empty objects while preserving hierarchy",
    "category": "Object",
}

import bpy
from bpy.types import Operator, Panel

class CONVERT_OT_empties_to_collections(Operator):
    bl_idname = "object.organize_empties_to_collections"
    bl_label = "Organize Empties to Collections"
    bl_description = "Create collections for empty objects and move their hierarchies"
    bl_options = {'REGISTER', 'UNDO'}
    
    def get_full_hierarchy(self, obj):
        """
        Get an object and its entire hierarchy of children recursively,
        similar to Blender's Select Hierarchy function.
        """
        def collect_children(parent, hierarchy):
            for child in bpy.data.objects:
                if child.parent == parent:
                    hierarchy.add(child)
                    collect_children(child, hierarchy)
        
        hierarchy = {obj}
        collect_children(obj, hierarchy)
        return hierarchy

    def execute(self, context):
        try:
            # Find all top-level empties
            top_level_empties = [obj for obj in bpy.data.objects 
                               if obj.type == 'EMPTY' and obj.parent is None]
            
            if not top_level_empties:
                self.report({'WARNING'}, "No top-level empty objects found")
                return {'CANCELLED'}
            
            collections_created = 0
            for empty in top_level_empties:
                # Create new collection with empty's name
                collection = bpy.data.collections.new(empty.name)
                context.scene.collection.children.link(collection)
                
                # Get the entire hierarchy under this empty
                hierarchy = self.get_full_hierarchy(empty)
                
                # Move all objects in the hierarchy to the new collection
                for obj in hierarchy:
                    # Unlink from current collections
                    for col in obj.users_collection:
                        col.objects.unlink(obj)
                    # Link to new collection
                    collection.objects.link(obj)
                collections_created += 1
            
            self.report({'INFO'}, f"Successfully created {collections_created} collections")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error during conversion: {str(e)}")
            return {'CANCELLED'}

class VIEW3D_PT_empty_converter_panel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    bl_label = "Empty Convert"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        # Add conversion button
        row = layout.row()
        row.operator(CONVERT_OT_empties_to_collections.bl_idname, 
                    text="Organize to Collections", 
                    icon='OUTLINER_COLLECTION')
        
        # Add information about the tool
        box = layout.box()
        col = box.column()
        col.label(text="This tool will:", icon='INFO')
        col.label(text="• Create collections for empties")
        col.label(text="• Move entire hierarchies")
        col.label(text="• Keep all parent relationships")
        col.label(text="• Preserve all transforms")

# Add to the Object menu
def menu_func(self, context):
    self.layout.operator(CONVERT_OT_empties_to_collections.bl_idname)

classes = (
    CONVERT_OT_empties_to_collections,
    VIEW3D_PT_empty_converter_panel,
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
