import openmc 
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time

class DetailedModel:

    def __init__(self):

        print("Creating model...")
        self.material_list = []
        self.cell_list = []
        self.tally_list = []
        self.foil_dict = {}
        self.air_regions_list = []
        self.key_surfaces = {}

        self.create_materials()
        self.build_outer()
        self.build_target()
        self.build_vacuum()
        self.build_structure()
        self.build_walls()
        self.update_geometry()
        

    def create_materials(self):

        # create basic material
        titanium = openmc.Material(name='Titanium')
        titanium.add_element('Ti', 1.0)
        titanium.set_density('g/cm3', 4.506)

        copper = openmc.Material(name='Copper')
        copper.add_element('Cu', 1.0)
        copper.set_density('g/cm3', 8.96)

        h2o = openmc.Material(name='Water')
        h2o.add_nuclide('H1', 2.0)
        h2o.add_nuclide('O16', 1.0)
        h2o.add_s_alpha_beta('c_H_in_H2O')
        h2o.set_density('g/cm3', 1.0)

        li7 = openmc.Material(name='Lithium')
        li7.add_nuclide('Li7', 1.0)
        li7.set_density('g/cm3', 0.534)

        graphite = openmc.Material(name='Graphite')
        graphite.add_element('C', 1.0)
        graphite.set_density('g/cm3', 2.1)
        graphite.add_s_alpha_beta('c_Graphite')

        iron = openmc.Material(name='Iron')
        iron.add_element('Fe', 1.0)
        iron.set_density('g/cm3', 7.874)

        vacuum = openmc.Material(name='Vacuum')
        vacuum.add_nuclide('H1', 1.0)
        vacuum.set_density('g/cm3', 0.0001)

        # Portland cement, ths same as G4_CONCRETE
        concrete = openmc.Material(name='Concrete')
        concrete.add_element('H', 0.01, 'wo')
        concrete.add_element('C', 0.001, 'wo')
        concrete.add_element('O', 0.529107, 'wo')
        concrete.add_element('Na', 0.016, 'wo')
        concrete.add_element('Mg', 0.002, 'wo')
        concrete.add_element('Al', 0.0338721, 'wo')
        concrete.add_element('Si', 0.337021, 'wo')
        concrete.add_element('K', 0.013, 'wo')
        concrete.add_element('Ca', 0.044, 'wo')
        concrete.add_element('Fe', 0.014, 'wo')
        concrete.set_density('g/cm3', 2.3)

        # Boronated plastic (G4_POLYETHYLENE)
        polyethylene = openmc.Material(name='Polyethylene')
        polyethylene.add_element('H', 0.143716, 'wo')
        polyethylene.add_element('C', 0.856284, 'wo')
        polyethylene.set_density('g/cm3', 1.03)

        boron = openmc.Material(name='Boron')
        boron.add_element('B', 1.0)
        boron.set_density('g/cm3', 2.37)

        # 5% mixture of boron into polyethylene
        boronated_polyethylene = openmc.Material.mix_materials([polyethylene, boron], [0.95, 0.05] ,'wo', name='Boronated Polyethylene')

        # Lead
        lead = openmc.Material(name='Lead')
        lead.add_element('Pb', 0.986, 'wo')
        lead.add_element('Bi', 0.012, 'wo')
        lead.add_element('Ag', 0.002, 'wo')
        lead.set_density('g/cm3', 11.34)

        # Air
        air = openmc.Material(name='Air')
        air.add_element('N', 0.78)
        air.add_element('O', 0.21)
        air.add_element('Ar', 0.01)
        air.set_density('g/cm3', 1.225E-3)

        co59 = openmc.Material(name='Cobalt')
        co59.add_nuclide('Co59', 1.0)
        co59.set_density('g/cm3', 8.86)

        self.material_list = [titanium, copper, h2o, li7, graphite, iron, vacuum, concrete, boronated_polyethylene, air, lead, co59]
        self.materials_dict = {m.name : m for m in self.material_list}
        materials = openmc.Materials(self.material_list)
        materials.export_to_xml()


    def add_material(self, material):
        
        if material.name == '':
            print('Please provide a name for reference')
        else:
            self.material_list.append(material)
            self.materials_dict[material.name] = material
            materials = openmc.Materials(self.material_list)
            materials.export_to_xml()
            print(f'Added {material.name} to materials list')


    def output_materials(self):

        print(f'Materials in model:\n{list(self.materials_dict.keys())}')

    def get_material(self, mat_name):

        try:
            return self.materials_dict[mat_name]
        except KeyError:
            print(f"Material {mat_name} not found. Check capitalisation / spelling. Use 'output_materials()' method to see all available materials.")
        

    def build_outer(self):

        # Outer titanium surfaces
        outer_cyl = openmc.ZCylinder(x0=0, y0=0, r=55.5)
        outer_top = openmc.YPlane(y0=55.5)
        outer_bottom = openmc.YPlane(y0=-55.5)
        outer_left = openmc.XPlane(x0=-55.5)
        outer_right = openmc.XPlane(x0=55.5)
        outer_mid_horizontal = openmc.YPlane(y0=-35.0)
        outer_mid_vert_left = openmc.XPlane(x0=-25.5)
        outer_mid_vert_right = openmc.XPlane(x0=25.5)
        outer_front = openmc.ZPlane(z0=4.56)
        self.key_surfaces['Vessel Front'] = [0,0,4.56]
        outer_back = openmc.ZPlane(z0=-5.04)
        # Main wheel section to remove
        outer_inside_cyl = openmc.ZCylinder(x0=0, y0=0, r=51.7)
        outer_inside_front = openmc.ZPlane(z0=1.56)
        outer_inside_back = openmc.ZPlane(z0=-1.14)
        # Square region to remove for graphite plates
        graphite_remove_front = openmc.ZPlane(z0=3.96)
        graphite_remove_left = openmc.XPlane(x0=-8.5)
        graphite_remove_right = openmc.XPlane(x0=8.5)
        graphite_remove_top = openmc.YPlane(y0=-33.5)
        graphite_remove_bottom = openmc.YPlane(y0=-50.5)
        # Cylinders for spindle and beampipe to remove
        spindle_remove_cyl = openmc.ZCylinder(x0=0, y0=0, r=9.3)
        bpipe_remove_cyl = openmc.ZCylinder(x0=0, y0=-42, r=8.5)

        # Define regions
        outer_region_full = ((-outer_top & +outer_mid_horizontal & +outer_left & -outer_right) | (-outer_cyl) | (+outer_bottom & -outer_mid_vert_right & +outer_mid_vert_left & -outer_mid_horizontal)) & +outer_back & -outer_front
        outer_region_subtract_1 = -outer_inside_cyl & -outer_inside_front & +outer_inside_back
        outer_region_subtract_2 = -graphite_remove_top & +graphite_remove_bottom & -graphite_remove_right & +graphite_remove_left & -graphite_remove_front & +outer_inside_front
        outer_region_subtract_3 = -spindle_remove_cyl & -outer_inside_back & +outer_back
        outer_region_subtract_4 = -bpipe_remove_cyl & +outer_back & -outer_inside_back
        outer_region = outer_region_full & ~outer_region_subtract_2 & ~outer_region_subtract_1 & ~outer_region_subtract_3 & ~outer_region_subtract_4

        # Create cell
        outer_cell = openmc.Cell(region=outer_region, fill=self.materials_dict['Titanium'], name='Titanium Cell')
        self.cell_list.append(outer_cell)

        # Beampipe DISPLACED 42cm VERTICALLY DOWNWARDS FROM ORIGIN
        bpipe_inner_cyl_1 = openmc.ZCylinder(x0=0, y0=-42, r=7.0)
        bpipe_inner_cyl_2 = openmc.ZCylinder(x0=0, y0=-42, r=6.0)
        bpipe_middle_cyl = openmc.ZCylinder(x0=0, y0=-42, r=7.5)
        bpipe_outer_cyl = openmc.ZCylinder(x0=0, y0=-42, r=8.5)

        bpipe_back = openmc.ZPlane(z0=-112.34)
        bpipe_midplane = openmc.ZPlane(z0=-31.14)

        bpipe_region_inner_1 = +bpipe_back & -bpipe_midplane & +bpipe_inner_cyl_2 & -bpipe_middle_cyl
        bpipe_region_inner_2 = +bpipe_midplane & -outer_inside_back & +bpipe_inner_cyl_1 & -bpipe_middle_cyl
        bpipe_region_outer = +bpipe_back & -outer_inside_back & +bpipe_middle_cyl & -bpipe_outer_cyl

        bpipe_cell_1 = openmc.Cell(fill=self.materials_dict['Graphite'], region = bpipe_region_inner_1 | bpipe_region_inner_2)
        self.cell_list.append(bpipe_cell_1)
        bpipe_cell_2 = openmc.Cell(fill=self.materials_dict['Titanium'], region=bpipe_region_outer)
        self.cell_list.append(bpipe_cell_2)

        graph_1_front = openmc.ZPlane(z0=3.56)
        graph_1_back = openmc.ZPlane(z0=3.21)
        graph_2_front = openmc.ZPlane(z0=2.76)
        graph_2_back = openmc.ZPlane(z0=2.41)

        graph_top = openmc.YPlane(y0=-33.75)
        graph_bottom = openmc.YPlane(y0=-50.25)
        graph_left = openmc.XPlane(x0=-8.25)
        graph_right = openmc.XPlane(x0=8.25)

        graphite_region_1 = -graph_top & +graph_bottom & -graph_right & +graph_left & +graph_1_back & -graph_1_front
        graphite_region_2 = -graph_top & +graph_bottom & -graph_right & +graph_left & +graph_2_back & -graph_2_front

        graphite_cell_1 = openmc.Cell(fill=self.materials_dict['Graphite'], region=graphite_region_1)
        self.cell_list.append(graphite_cell_1)
        graphite_cell_2 = openmc.Cell(fill=self.materials_dict['Graphite'], region=graphite_region_2)
        self.cell_list.append(graphite_cell_2)

        # Global export of regions to define vacuum
        self.bpipe_full = -bpipe_outer_cyl & +bpipe_back & -outer_inside_back
        self.outer_region = (outer_region | bpipe_region_inner_1 | bpipe_region_inner_2 | bpipe_region_outer | graphite_region_1 | graphite_region_2 )
        self.outer_region_full = outer_region_full

    def build_target(self):

        # Thin target region
        thin_cu_cyl_outer = openmc.ZCylinder(r=48.5)
        thin_cy_cyl_inner = openmc.ZCylinder(r=35.5)
        thin_cu_back = openmc.ZPlane(z0=0.01)
        thin_cu_front = openmc.ZPlane(z0=0.41)
        thin_water_back = openmc.ZPlane(z0=0.1575)
        thin_water_front = openmc.ZPlane(z0=0.2625)

        thin_cu_region = (-thin_cu_cyl_outer & +thin_cy_cyl_inner & +thin_cu_back & -thin_cu_front)# & ~(-thin_cu_cyl_outer & +thin_water_back & -thin_water_front)

        # Water channel 1 (end piece, smaller)
        cu_channel_1_outer = openmc.ZCylinder(r=50.95)
        cu_channel_1_back = openmc.ZPlane(z0=-0.34)
        cu_channel_1_front = openmc.ZPlane(z0=0.76)

        water_channel_1_outer = openmc.ZCylinder(r=50.5)
        water_channel_1_inner = openmc.ZCylinder(r=49)

        # Water channel 2 (middle piece, larger)
        cu_channel_2_outer = openmc.ZCylinder(r=35.5)
        cu_channel_2_inner = openmc.ZCylinder(r=28.9)
        cu_channel_2_back = openmc.ZPlane(z0=-0.49)
        cu_channel_2_front = openmc.ZPlane(z0=0.91)

        water_channel_2_inner = openmc.ZCylinder(r=29.9)
        water_channel_2_outer = openmc.ZCylinder(r=34.5)
        water_channel_2_back = openmc.ZPlane(z0=-0.015)
        water_channel_2_front = openmc.ZPlane(z0=0.435)

        # Water surfaces
        water_central_outer = openmc.ZCylinder(r=28.4)
        water_central_back = openmc.ZPlane(z0=0.04)
        water_central_front = openmc.ZPlane(z0=0.46)

        cu_channel_1_region = (-cu_channel_1_outer & +thin_cu_cyl_outer & +cu_channel_1_back & -cu_channel_1_front)# & ~(-water_channel_1_outer & +water_channel_1_inner & +thin_cu_back & -thin_cu_front)
        channel_1_water_region = (-water_channel_1_outer & +water_channel_1_inner & +thin_cu_back & -thin_cu_front)

        cu_channel_2_region = (-cu_channel_2_outer & +cu_channel_2_inner & +cu_channel_2_back & -cu_channel_2_front)# & ~(-water_channel_2_outer & +water_channel_2_inner & +thin_cu_back & -thin_cu_front)
        channel_2_water_region = -water_channel_2_outer & +water_channel_2_inner & +water_channel_2_back & -water_channel_2_front

        thin_water_region = (-water_channel_1_inner & +water_channel_2_outer & +thin_water_back & -thin_water_front)

        cu_region = (thin_cu_region | cu_channel_1_region | cu_channel_2_region) & ~channel_1_water_region & ~channel_2_water_region & ~thin_water_region

        cu_cell = openmc.Cell(fill=self.materials_dict['Copper'], region = cu_region, name='Copper Cell')
        self.cell_list.append(cu_cell)

        water_central_region = -water_central_outer & +water_central_back & -water_central_front
        water_target_region = channel_1_water_region | channel_2_water_region | thin_water_region
        central_water_cell = openmc.Cell(fill=self.materials_dict['Water'], region = water_central_region)
        self.cell_list.append(central_water_cell)
        water_target_cell = openmc.Cell(fill=self.materials_dict['Water'], region = water_target_region)
        self.cell_list.append(water_target_cell)

        #cu1 = openmc.Geometry([cu_cell, water_target_cell])
        #cu1.plot((0,-42,0), width=(25,2.5), pixels=(400,400), basis='yz')
        #plt.show()

        # Lithium
        lithium_back = openmc.ZPlane(z0=-0.01)
        lithium_region = +lithium_back & -thin_cu_back & -thin_cu_cyl_outer & +thin_cy_cyl_inner
        lithium_cell = openmc.Cell(fill=self.materials_dict['Lithium'], region = lithium_region)
        self.cell_list.append(lithium_cell)

        # Inner titanium
        inner_titanium_back = openmc.ZPlane(z0=-1.04)
        inner_titanium_front = openmc.ZPlane(z0=1.46)

        inner_titanium_region_1 = +inner_titanium_back & -water_central_back & -water_central_outer
        inner_titanium_region_2 = +water_central_front & -inner_titanium_front & -water_central_outer

        inner_titanium_cell_1 = openmc.Cell(fill=self.materials_dict['Titanium'], region = inner_titanium_region_1)
        self.cell_list.append(inner_titanium_cell_1)
        inner_titanium_cell_2 = openmc.Cell(fill=self.materials_dict['Titanium'], region = inner_titanium_region_2)
        self.cell_list.append(inner_titanium_cell_2)

        # Tail water
        tail_water_outer_cyl = openmc.ZCylinder(r=2.5)
        tail_water_back = openmc.ZPlane(z0=-64.54)

        tail_water_region = +tail_water_back & -tail_water_outer_cyl & -inner_titanium_back
        tail_water_cell = openmc.Cell(fill=self.materials_dict['Water'], region=tail_water_region)
        self.cell_list.append(tail_water_cell)

        # Ferro
        ferro_cyl_1 = openmc.ZCylinder(r=9)
        ferro_cyl_2 = openmc.ZCylinder(r=4.6)
        ferro_cyl_3 = openmc.ZCylinder(r=12.7)
        ferro_cyl_4 = openmc.ZCylinder(r=8.1)
        ferro_cyl_5 = openmc.ZCylinder(r=3.2485)

        ferro_inner_cyl = openmc.ZCylinder(r=2.5)

        ferro_front = openmc.ZPlane(z0=-1.04)
        ferro_plane_1 = openmc.ZPlane(z0=-2.54)
        ferro_plane_2 = openmc.ZPlane(z0=-5.04)
        ferro_plane_3 = openmc.ZPlane(z0=-7.54)
        ferro_plane_4 = openmc.ZPlane(z0=-20.04)
        ferro_back = openmc.ZPlane(z0=-31.74)

        ferro_region_1 = -ferro_cyl_1 & -ferro_front & +ferro_plane_1
        ferro_region_2 = -ferro_cyl_2 & -ferro_plane_1 & +ferro_plane_2
        ferro_region_3 = -ferro_cyl_3 & -ferro_plane_2 & +ferro_plane_3
        ferro_region_4 = -ferro_cyl_4 & -ferro_plane_3 & +ferro_plane_4
        ferro_region_5 = -ferro_cyl_5 & -ferro_plane_4 & +ferro_back

        ferro_full_region = ferro_region_1 | ferro_region_2 | ferro_region_3 | ferro_region_4 | ferro_region_5

        ferro_region = ferro_full_region & ~tail_water_region

        ferro_cell = openmc.Cell(fill=self.materials_dict['Iron'], region = ferro_region)
        self.cell_list.append(ferro_cell)

        tpipe_back = openmc.ZPlane(z0=-67.94)
        tpipe_water_back = openmc.ZPlane(z0=-64.54)
        tpipe_outer_cyl = openmc.ZCylinder(r=5)

        tpipe_region = (+tpipe_back & -tpipe_outer_cyl & -ferro_back) & ~ (+tpipe_water_back & -ferro_inner_cyl & -ferro_back)

        tpipe_cell = openmc.Cell(fill = self.materials_dict['Titanium'], region = tpipe_region)
        self.cell_list.append(tpipe_cell)

        # Global export of regions to define vacuum
        self.target_region = (ferro_region | tail_water_region | tpipe_region | cu_region | lithium_region | thin_cu_region | thin_water_region | channel_1_water_region | channel_2_water_region | inner_titanium_region_2 
                                            | inner_titanium_region_1 | water_central_region | water_target_region | cu_channel_2_region | cu_channel_1_region)


    def build_vacuum(self):

        # For this, we make a region with the full outer bounds of the shape that can contain vacuum, and then remove every region that is defined inside this
        self.full_model_region = self.outer_region_full | self.bpipe_full | self.target_region
        #fmcell = openmc.Cell(fill=self.materials_dict['Titanium'], region=self.full_model_region)
        #self.geometry = openmc.Geometry([fmcell])
        #self.geometry.plot((0,0,-55), width=(120, 130), pixels=(1000,1000), basis='yz', color_by='material', outline=False)
        #plt.title('x-z view')
        #plt.show()

        vacuum_region = self.full_model_region & ~(self.outer_region | self.target_region)
        vacuum_cell = openmc.Cell(fill=self.materials_dict['Vacuum'], region=vacuum_region)
        self.cell_list.append(vacuum_cell)

    def build_structure(self):

        floor = openmc.YPlane(y0=-162.0)

        # Left Concrete Block
        concrete_L_left = openmc.XPlane(x0=-118.0)
        concrete_L_right = openmc.XPlane(x0=-78.0)
        concrete_L_front = openmc.ZPlane(z0=84.1)
        concrete_L_back = openmc.ZPlane(z0=-75.9)
        concrete_L_top = openmc.YPlane(y0=58.0)

        concrete_block_L_region = +concrete_L_left & -concrete_L_right & +floor & -concrete_L_top & -concrete_L_front & +concrete_L_back
        concrete_block_L_cell = openmc.Cell(fill=self.materials_dict['Concrete'], region=concrete_block_L_region)
        self.cell_list.append(concrete_block_L_cell)

        # Right Concrete Block
        concrete_R_right = openmc.XPlane(x0=122.5)
        concrete_R_left = openmc.XPlane(x0=82.5)
        concrete_R_front = openmc.ZPlane(z0=114.1)
        concrete_R_back = openmc.ZPlane(z0=-45.9)
        concrete_R_top = openmc.YPlane(y0=58.0)

        concrete_block_R_region = +concrete_R_left & -concrete_R_right & +floor & -concrete_R_top & -concrete_R_front & +concrete_R_back
        concrete_block_R_cell = openmc.Cell(fill=self.materials_dict['Concrete'], region=concrete_block_R_region)
        self.cell_list.append(concrete_block_R_cell)

        # Left boronated plastic
        N_sheets_L = 2
        plastic_L_right = openmc.XPlane(x0=-78.0+2.5*N_sheets_L)

        plastic_L_region = +concrete_L_right & -plastic_L_right & +floor & -concrete_L_top & +concrete_L_back & -concrete_L_front
        plastic_L_cell = openmc.Cell(fill=self.materials_dict['Boronated Polyethylene'], region=plastic_L_region)
        self.cell_list.append(plastic_L_cell)

        # Right boronated plastic
        N_sheets_R = 3
        plastic_R_left = openmc.XPlane(x0=82.5-2.5*N_sheets_R)

        plastic_R_region = -concrete_R_left & +plastic_R_left & +floor & -concrete_R_top & +concrete_R_back & -concrete_R_front
        plastic_R_cell = openmc.Cell(fill=self.materials_dict['Boronated Polyethylene'], region=plastic_R_region)
        self.cell_list.append(plastic_R_cell)

        # Centre concrete
        concrete_C_front = openmc.ZPlane(z0=49.6)
        concrete_C_mid_h = openmc.ZPlane(z0=32.6)
        concrete_C_back = openmc.ZPlane(z0=9.6)
        concrete_C_left = openmc.XPlane(x0=-40.0)
        concrete_C_right = openmc.XPlane(x0=40.0)
        concrete_C_top = openmc.YPlane(y0=-59.0)
        concrete_C_mid_v = openmc.YPlane(y0=-82)

        concrete_C_region = (+floor & -concrete_C_top & +concrete_C_left & -concrete_C_right & +concrete_C_back & -concrete_C_front) & ~(+concrete_C_mid_v & -concrete_C_top & +concrete_C_left & -concrete_C_right & -concrete_C_front & +concrete_C_mid_h)
        concrete_C_cell = openmc.Cell(fill=self.materials_dict['Concrete'], region=concrete_C_region)
        self.cell_list.append(concrete_C_cell)

        iron_plate_top = openmc.YPlane(y0=-56.5)
        self.key_surfaces['Plate Top'] = [0, -56.5, 0]
        iron_plate_left = openmc.XPlane(x0=-45.0)
        iron_plate_right = openmc.XPlane(x0=45.0)
        iron_plate_back = openmc.ZPlane(z0=4.6)

        iron_plate_region = +iron_plate_back & -concrete_C_mid_h & +concrete_C_top & -iron_plate_top & +iron_plate_left & -iron_plate_right
        iron_plate_cell = openmc.Cell(fill=self.materials_dict['Iron'], region=iron_plate_region)
        self.cell_list.append(iron_plate_cell)

        # Lead shielding
        lead_left = openmc.XPlane(x0=-60.5)
        lead_right = openmc.XPlane(x0=60.5)
        lead_back = openmc.ZPlane(z0=6.1)
        lead_thickness = 12.0
        lead_front = openmc.ZPlane(z0=6.1 + lead_thickness)
        lead_top = openmc.YPlane(y0=55.5)
        lead_corner_v = openmc.XPlane(x0=-10.5)
        lead_corner_h = openmc.YPlane(y0=15.6)
        lead_cutout_left = openmc.XPlane(x0=-11.5)
        self.key_surfaces['Lead Opening Left'] = [-11.5, 0, 0]
        lead_cutout_right = openmc.XPlane(x0=11.5)
        self.key_surfaces['Lead Opening Right'] = [11.5, 0, 0]
        lead_cutout_top = openmc.YPlane(y0=-30.5)
        self.key_surfaces['Lead Opening Top'] = [0, -30.5, 0]

        lead_region = (+lead_left & -lead_right & +lead_back & -lead_front & +iron_plate_top & -lead_top) & ~(+lead_corner_h & -lead_corner_v) & ~(-lead_cutout_top & +lead_cutout_left & -lead_cutout_right)
        lead_cell = openmc.Cell(fill=self.materials_dict['Lead'], region=lead_region)
        self.cell_list.append(lead_cell)

        # Graphite region behind target
        graph_block_top = openmc.YPlane(y0=-56.35)
        graph_block_bottom = openmc.YPlane(y0=-136.35)
        self.key_surfaces['Graphite Bottom'] = [0, -136.35, 0]
        graph_block_front = openmc.ZPlane(z0=-4.56)
        graph_block_back = openmc.ZPlane(z0=-58.94)
        graph_block_left = openmc.XPlane(x0=-50)
        graph_block_right = openmc.XPlane(x0=50)

        graph_block_region = (+graph_block_left & -graph_block_right & +graph_block_bottom & -graph_block_top & +graph_block_back & -graph_block_front)
        graph_block_cell = openmc.Cell(fill=self.materials_dict['Graphite'], region=graph_block_region)
        self.cell_list.append(graph_block_cell)

        # Global export of regions to define vacuum
        self.structure_region = lead_region | iron_plate_region | concrete_C_region | plastic_R_region | plastic_L_region | concrete_block_R_region | concrete_block_L_region | graph_block_region


    def build_walls(self):

        # Rear wall
        rear_wall_front = openmc.ZPlane(z0=-113.44)
        rear_wall_mid = openmc.ZPlane(z0=-115.94)
        rear_wall_back = openmc.ZPlane(z0=-268.34, boundary_type='vacuum')
        # Front wall
        front_wall_front = openmc.ZPlane(z0=408.6)
        front_wall_mid = openmc.ZPlane(z0=411.11)
        front_wall_back = openmc.ZPlane(z0=563.51, boundary_type='vacuum')
        # Left wall
        R_wall_front = openmc.XPlane(x0=217.5)
        R_wall_mid = openmc.XPlane(x0=220.0)
        R_wall_back = openmc.XPlane(x0=372.4, boundary_type='vacuum')
        # Right wall
        L_wall_front = openmc.XPlane(x0=-222.9)
        L_wall_mid = openmc.XPlane(x0=-225.4)
        L_wall_back = openmc.XPlane(x0=-380.3, boundary_type='vacuum')
        # Floor
        floor_top = openmc.YPlane(y0=-162.0)
        floor_bottom = openmc.YPlane(y0=-314.4, boundary_type='vacuum')
        # Ceiling
        ceiling_bottom = openmc.YPlane(y0=135.0)
        ceiling_top = openmc.YPlane(y0=287.4, boundary_type='vacuum')

        full_concrete_region = +rear_wall_back & -front_wall_back & +L_wall_back & -R_wall_back & +floor_bottom & -ceiling_top
        full_plastic_region = +rear_wall_mid & -front_wall_mid & +L_wall_mid & -R_wall_mid & +floor_top & -ceiling_bottom
        full_air_region = +rear_wall_front & -front_wall_front & +L_wall_front & -R_wall_front & +floor_top & -ceiling_bottom
        concrete_region = full_concrete_region & ~full_plastic_region
        plastic_region = full_plastic_region & ~full_air_region
        self.air_region = full_air_region & ~(self.full_model_region | self.structure_region)
        self.air_regions_list.append(self.air_region)

        #fmcell = openmc.Cell(fill=self.materials_dict['Titanium'], region=air_region)
        #self.geometry = openmc.Geometry([fmcell])
        #self.geometry.plot((0,0,0), width=(500, 500), pixels=(1000,1000), basis='yz', color_by='material', outline=False)
        #plt.title('x-z view')
        #plt.show()

        concrete_cell = openmc.Cell(fill=self.materials_dict['Concrete'], region=concrete_region)
        self.cell_list.append(concrete_cell)
        plastic_cell = openmc.Cell(fill=self.materials_dict['Boronated Polyethylene'], region=plastic_region)
        self.cell_list.append(plastic_cell)
        self.air_cell = openmc.Cell(fill=self.materials_dict['Air'], region=self.air_region)
        self.cell_list.append(self.air_cell)


    def get_key_surface(self, surface_name):

        try:
            return self.key_surfaces[surface_name]
        except KeyError:
            print(f"Surface {surface_name} not found. Check capitalisation / spelling. Use 'output_surfaces()' method to see all available surfaces.")
    

    def output_surfaces(self):

        print(f'Surfaces in model:\n{list(self.key_surfaces.keys())}')


    def add_cell(self, new_cell):


        # Get required properties of new cell
        cell_name = new_cell.name
        cell_region = new_cell.region
        # Update air region to not include this new cell
        self.air_region = self.air_region & ~cell_region
        # Add new cell to required list + dictionary
        self.cell_list.append(new_cell)
        self.foil_dict[cell_name] = new_cell
        # Run function to update the air to the new region
        self.update_air()

    
    def remove_cell(self, cell_name):

        # Find cell by name
        for i, cell in enumerate(self.cell_list):

            #print(i, cell.name)
            if cell.name == cell_name:

                old_cell = cell
                old_region = old_cell.region
                self.air_region = self.air_region | old_region
                self.cell_list.pop(i)
                print(f'removed {cell.name}')
                break
        
        self.update_air()
        


    def update_air(self):

        # Get index of current air cell
        air_cell_index = self.cell_list.index(self.air_cell)
        print(air_cell_index)
        self.air_cell = openmc.Cell(fill=self.materials_dict['Air'], region = self.air_region)
        self.cell_list[air_cell_index] = self.air_cell
        self.update_geometry()


    
    def add_square_foil(self, foil_name, foil_width, foil_height, foil_thickness, foil_material,  foil_position = [0,0,0]):
        """Use this function to define a foil which can be placed inside the air volume in the room.
        Note: Foil position defaults to flush with edge of titanium, along axis of beam, so adjust position relative to this point.
        Please define a material separately using 'create_material' and reference by name.

        Args:
            foil_region (openmc.Region): This should be made up of the 
            foil_material (str): Name of foil material, defined in foil list/dictionary
        """
        foil_start = openmc.ZPlane(z0=4.56 + foil_position[2])
        foil_end = openmc.ZPlane(z0=4.56 + foil_position[2] + foil_thickness)
        foil_left = openmc.XPlane(x0=foil_position[0] -foil_width/2)
        foil_right = openmc.XPlane(x0=foil_position[0] + foil_width/2)
        foil_bottom = openmc.YPlane(y0=foil_position[1] - foil_height/2 - 42)
        foil_top = openmc.YPlane(y0=foil_position[1] + foil_height/2 - 42)
        foil_region = +foil_left & -foil_right & +foil_bottom & -foil_top & +foil_start & -foil_end
        foil_cell = openmc.Cell(region=foil_region, fill=self.materials_dict[foil_material], name=foil_name)
        self.cell_list.append(foil_cell)
        self.foil_dict[foil_name] = foil_cell
        self.update_air_old(foil_region)
        print(f'Added new foil at x = {foil_position[0]}, y = {foil_position[1]- 42}, z = {4.56 + foil_position[2] + foil_thickness/2}')
    
    def add_circle_foil(self, foil_name, foil_radius, foil_thickness, foil_material,  foil_position = [0,0,0]):
        """Use this function to define a foil which can be placed inside the air volume in the room.
        Note: Foil position defaults to flush with edge of titanium, along axis of beam, so adjust position relative to this point.
        Please define a material separately using 'create_material' and reference by name.

        Args:
            foil_region (openmc.Region): This should be made up of the 
            foil_material (str): Name of foil material, defined in foil list/dictionary
        """
        c_foil_start = openmc.ZPlane(z0=4.56 + foil_position[2])
        c_foil_end = openmc.ZPlane(z0=4.56 + foil_position[2] + foil_thickness)
        c_foil_edge = openmc.ZCylinder(x0=foil_position[0], y0=foil_position[1] - 42, r=foil_radius)
        c_foil_region = -c_foil_edge & +c_foil_start & -c_foil_end
        c_foil_cell = openmc.Cell(region=c_foil_region, fill=self.materials_dict[foil_material], name=foil_name)
        self.cell_list.append(c_foil_cell)
        self.foil_dict[foil_name] = c_foil_cell
        self.update_air_old(c_foil_region)
        print(f'Added new circular foil id: {self.cell_list}')


    def update_air_old(self, new_region):
        
        # Get index of current air cell
        air_cell_index = self.cell_list.index(self.air_cell)
        print(air_cell_index)
        air_region_updated = self.air_region & ~new_region
        self.air_region = air_region_updated
        self.air_regions_list.append(air_region_updated)
        self.air_cell = openmc.Cell(fill=self.materials_dict['Air'], region = self.air_region)
        self.cell_list[air_cell_index] = self.air_cell
        self.update_geometry()


        #cu1 = openmc.Geometry([self.air_cell])
        #cu1.plot((0,-42,0), width=(100,100), pixels=(400,400), basis='yz')
        #plt.show()

    def undo_air(self, old_region):
        '''
        Reverts most recent update of air region to previous region, updates cell accordingly
        '''

        # Get index of current air cell
        air_cell_index = self.cell_list.index(self.air_cell)
        # Remove most recent region from list
        self.air_regions_list.pop()
        # Set air region to new final region
        self.air_region = self.air_regions_list[-1]
        self.air_cell = openmc.Cell(fill=self.materials_dict['Air'], region = self.air_region)
        self.cell_list[air_cell_index] = self.air_cell
        self.update_geometry()

    def update_geometry(self):

        geometry = openmc.Geometry(self.cell_list)
        geometry.export_to_xml()


    def add_block(self, block_name, block_width, block_height, block_thickness, block_material,  block_position = [0,0,0]):

        """Use this function to define a foil which can be placed inside the air volume in the room.
        Note: Foil position defaults to flush with edge of titanium, along axis of beam, so adjust position relative to this point.
        Please define a material separately using 'create_material' and reference by name.

        Args:
            foil_region (openmc.Region): This should be made up of the 
            foil_material (str): Name of foil material, defined in foil list/dictionary
        """
        block_start = openmc.ZPlane(z0=4.56 + block_position[2])
        block_end = openmc.ZPlane(z0=4.56 + block_position[2] + block_thickness)
        block_left = openmc.XPlane(x0=block_position[0] -block_width/2)
        block_right = openmc.XPlane(x0=block_position[0] + block_width/2)
        block_bottom = openmc.YPlane(y0=block_position[1] - block_height/2 - 42)
        block_top = openmc.YPlane(y0=block_position[1] + block_height/2 - 42)
        block_region = +block_left & -block_right & +block_bottom & -block_top & +block_start & -block_end
        block_cell = openmc.Cell(region=block_region, fill=self.materials_dict[block_material], name=block_name)
        self.cell_list.append(block_cell)
        self.foil_dict[block_name] = block_cell
        self.update_air_old(block_region)
        print(f'Added new foil at x = {block_position[0]}, y = {block_position[1]- 42}, z = {4.56 + block_position[2] + block_thickness/2}')
    
    def remove_block(self, block_name):

        #print(self.cell_list)
        #self.cell_remove_index = self.cell_list.index()

        for i, cell in enumerate(self.cell_list):

            print(i, cell.name)
            if cell.name == block_name:
                self.cell_list.pop(i)
                print(f'removed {cell.name}')
                break

        
                

    def plot_full(self, plane):

        self.geometry = openmc.Geometry(self.cell_list)

        if plane == 'xy':

            self.geometry.plot((-4,-13.5,0), width=(760, 610), pixels=(1000,1000), basis='xy', color_by='material', outline=False)
            plt.xlabel('x (cm)')
            plt.ylabel('y (cm)')
            plt.title('x-y view')
            plt.show()

        elif plane == 'xz':

            self.geometry.plot((-4,0,147.5), width=(760, 840), pixels=(1000,1000), basis='xz', color_by='material', outline=False)
            plt.xlabel('x (cm)')
            plt.ylabel('y (cm)')
            plt.title('x-z view')
            plt.show()

        elif plane == 'yz':

            self.geometry.plot((0,-13.5,147.5), width=(610, 840), pixels=(1000,1000), basis='yz', color_by='material', outline=False)
            plt.xlabel('x (cm)')
            plt.ylabel('y (cm)')
            plt.title('x-y view')
            plt.show()

        else:
            print('REPLACE WITH PROPER ERROR: Plotting plane incorrectly specified, should be "xy", "xz", "yz"')
        

    def plot(self):

        self.geometry = openmc.Geometry(self.cell_list)

        self.geometry.plot((0,-40,0), width=(200, 200), pixels=(1000,1000), basis='yz', color_by='material', outline=False)
        plt.title('x-z view')
        plt.show()

    def plot_zoomed(self, plane, centre, dimensions):
        '''self.geometry = openmc.Geometry(self.cell_list)

        self.geometry.plot((0,-138,-36), width=(5, 5), pixels=(2000,2000), basis='yz', color_by='material', outline=False)
        #plt.title('x-z view')
        plt.show()'''

        self.geometry = openmc.Geometry(self.cell_list)
        try:
            c1, c2 = centre[0], centre[1]
        except:
            print('PROPER ERROR: Centre coordinate incorrectly defined')

        try:
            d1, d2 = dimensions[0], dimensions[1]
        except:
            print('PROPER ERROR: Dimensions incorrectly defined')


        if plane == 'xy':

            self.geometry.plot((c1,c2,0), width=(d1, d2), pixels=(1000,1000), basis='xy', color_by='material', outline=False)
            plt.xlabel('x (cm)')
            plt.ylabel('y (cm)')
            plt.title('x-y view')
            plt.legend()
            plt.show()

        elif plane == 'xz':

            self.geometry.plot((d1,0,d2), width=(d1, d2), pixels=(1000,1000), basis='xz', color_by='material', outline=False)
            plt.xlabel('x (cm)')
            plt.ylabel('y (cm)')
            plt.title('x-z view')
            plt.show()

        elif plane == 'yz':

            self.geometry.plot((0,c1,c2), width=(d1, d2), pixels=(1000,1000), basis='yz', color_by='material', outline=False)
            plt.xlabel('x (cm)')
            plt.ylabel('y (cm)')
            plt.title('x-y view')
            plt.show()

        else:
            print('REPLACE WITH PROPER ERROR: Plotting plane incorrectly specified, should be "xy", "xz", "yz"')
        

    def plot_plane(self):

        self.geometry = openmc.Geometry(self.cell_list)

        self.geometry.plot((0,-42,4.661), width=(5, 5), pixels=(2000,2000), basis='xy', color_by='material', outline=False)
        plt.title('x-y view')
        plt.show()

    def setup_neutrons(self, Ep, N_neutrons, source = 'MCNP'):

        if source == 'MCNP':

            comp_source = openmc.CompiledSource(f'../fuente_LiMetal_Epmin_0_Epmax_{Ep}/build/libsource.so')
        elif source == 'BRUMLIT':
            comp_source = openmc.CompiledSource(f'/home/ADF/mjc970/Documents/High Flux Neutron Source/Python Module/hfadnef/hfadnef/build/libsource.so', Ep)

        else:
            raise Exception("Source not valid. Enter either:\n  - 'MCNP'\n  - 'BRUMLIT'")
        # Set up simulation
        settings = openmc.Settings()
        settings.source = comp_source
        settings.particles = N_neutrons
        settings.batches = 10
        settings.run_mode = 'fixed source'
        settings.max_tracks = 100_000
        settings.seed = time.time_ns()
        settings.export_to_xml()


    def setup_tallies(self, tally_cells, tally_score):

        for c in tally_cells:
            print(c)


    def add_tally(self, tally_name, tally_cell, tally_score, tally_filter=None, tally_nuclides = None):

        cell_filter = openmc.CellFilter(self.foil_dict[tally_cell])
        new_tally = openmc.Tally(name=tally_name)
        new_tally.scores = [tally_score]

        if tally_filter == None:
            new_tally.filters = [cell_filter]

        else:
            new_tally.filters = [cell_filter, tally_filter]

        if tally_nuclides != None:

            new_tally.nuclides = tally_nuclides

        self.tally_list.append(new_tally)
        tallies = openmc.Tallies(self.tally_list)
        tallies.export_to_xml()
        print(tallies)

    def clear_tallies(self):

        self.tally_list = []
        tallies = openmc.Tallies(self.tally_list)
        tallies.export_to_xml()


    def add_tally_ng_log(self, tally_name, tally_cell, E_filter):

        cell_filter = openmc.CellFilter(self.foil_dict[tally_cell])
        new_tally = openmc.Tally(name=tally_name)
        new_tally.scores = ['(n,gamma)']
        # Create log filter to convert energies
        E_points = np.linspace(0.00001, 0.25e6, 500)
        log_filter = openmc.EnergyFunctionFilter(E_points, np.log10(E_points))
        new_tally.filters = [cell_filter, log_filter, E_filter]

        self.tally_list.append(new_tally)
        tallies = openmc.Tallies(self.tally_list)
        tallies.export_to_xml()
        print(tallies)

        
    def run_model(self, track_bool=False):

        openmc.run(tracks=track_bool)