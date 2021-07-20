# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>

# Interface for this addon.


from bpy.types import Panel
import bmesh

from . import report


class View3DPrintPanel:
    bl_category = "3D-Print"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == 'MESH' and obj.mode in {'OBJECT', 'EDIT'}


class VIEW3D_PT_print3d_analyze(View3DPrintPanel, Panel):
    bl_label = "分析"

    _type_to_icon = {
        bmesh.types.BMVert: 'VERTEXSEL',
        bmesh.types.BMEdge: 'EDGESEL',
        bmesh.types.BMFace: 'FACESEL',
    }

    def draw_report(self, context):
        layout = self.layout
        info = report.info()

        if info:
            is_edit = context.edit_object is not None

            layout.label(text="結果")
            box = layout.box()
            col = box.column()

            for i, (text, data) in enumerate(info):
                if is_edit and data and data[1]:
                    bm_type, _bm_array = data
                    col.operator("mesh.print3d_select_report", text=text, icon=self._type_to_icon[bm_type],).index = i
                else:
                    col.label(text=text)

    def draw(self, context):
        layout = self.layout

        print_3d = context.scene.print_3d

        # TODO, presets

        layout.label(text="統計")
        row = layout.row(align=True)
        row.operator("mesh.print3d_info_volume", text="體積")
        row.operator("mesh.print3d_info_area", text="面積")

        layout.label(text="檢查")
        col = layout.column(align=True)
        col.operator("mesh.print3d_check_solid", text="實體")
        col.operator("mesh.print3d_check_intersect", text="交叉")
        row = col.row(align=True)
        row.operator("mesh.print3d_check_degenerate", text="退化")
        row.prop(print_3d, "threshold_zero", text="")
        row = col.row(align=True)
        row.operator("mesh.print3d_check_distort", text="扭曲")
        row.prop(print_3d, "angle_distort", text="")
        row = col.row(align=True)
        row.operator("mesh.print3d_check_thick", text="厚度")
        row.prop(print_3d, "thickness_min", text="")
        row = col.row(align=True)
        row.operator("mesh.print3d_check_sharp", text="銳利邊")
        row.prop(print_3d, "angle_sharp", text="")
        row = col.row(align=True)
        row.operator("mesh.print3d_check_overhang", text="懸空")
        row.prop(print_3d, "angle_overhang", text="")
        layout.operator("mesh.print3d_check_all", text="檢查全部")

        self.draw_report(context)


class VIEW3D_PT_print3d_cleanup(View3DPrintPanel, Panel):
    bl_label = "清理"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        print_3d = context.scene.print_3d

        row = layout.row(align=True)
        row.operator("mesh.print3d_clean_distorted", text="扭曲")
        row.prop(print_3d, "angle_distort", text="")
        layout.operator("mesh.print3d_clean_non_manifold", text="清理流形")
        # XXX TODO
        # layout.operator("mesh.print3d_clean_thin", text="Wall Thickness")


class VIEW3D_PT_print3d_transform(View3DPrintPanel, Panel):
    bl_label = "轉換"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        layout.label(text="縮放到")
        row = layout.row(align=True)
        row.operator("mesh.print3d_scale_to_volume", text="體積")
        row.operator("mesh.print3d_scale_to_bounds", text="界線")


class VIEW3D_PT_print3d_export(View3DPrintPanel, Panel):
    bl_label = "匯出"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        print_3d = context.scene.print_3d

        layout.prop(print_3d, "export_path", text="")

        col = layout.column()
        col.prop(print_3d, "use_apply_scale")
        col.prop(print_3d, "use_export_texture")

        layout.prop(print_3d, "export_format")
        layout.operator("mesh.print3d_export", text="匯出", icon='EXPORT')
