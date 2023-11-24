import bpy
from pathlib import Path
import numpy as np

from .load import create_molecule
from ..blender import nodes
from .. import assembly

bpy.types.Scene.MN_pdb_code = bpy.props.StringProperty(
    name = 'pdb_code', 
    description = 'The 4-character PDB code to download', 
    options = {'TEXTEDIT_UPDATE'}, 
    default = '1bna', 
    subtype = 'NONE', 
    maxlen = 4
    )
bpy.types.Scene.MN_cache_dir = bpy.props.StringProperty(
    name = 'cache_dir',
    description = 'Location to cache PDB files',
    options = {'TEXTEDIT_UPDATE'},
    default = str(Path('~', '.MolecularNodes').expanduser()),
    subtype = 'FILE_PATH'
)

def load(
    pdb_code,             
    style = 'spheres',               
    centre = False,               
    del_solvent = True,               
    setup_nodes = True,
    cache_dir = None,
    build_assembly = False
    ):
    from biotite import InvalidFileError
    mol, file = open_structure_rcsb(
        pdb_code = pdb_code, 
        cache_dir = cache_dir
        )
    
    mol, coll_frames = create_molecule(
        array = mol,
        name = pdb_code,
        file = file,
        calculate_ss = False,
        centre = centre,
        del_solvent = del_solvent, 
        )
    
    if setup_nodes:
        nodes.create_starting_node_tree(
            obj = mol, 
            coll_frames=coll_frames, 
            style = style
            )
    
    # mol['bio_transform_dict'] = file['bioAssemblyList']
    
    
    try:
        parsed_assembly_file = assembly.mmtf.MMTFAssemblyParser(file)
        mol['biological_assemblies'] = parsed_assembly_file.get_assemblies()
    except InvalidFileError:
        pass
    
    if build_assembly:
        obj = mol
        transforms_array = assembly.mesh.get_transforms_from_dict(obj['biological_assemblies'])
        data_object = assembly.mesh.create_data_object(
            transforms_array = transforms_array, 
            name = f"data_assembly_{obj.name}"
        )
        
        node_assembly = nodes.create_assembly_node_tree(
            name = obj.name, 
            iter_list = obj['chain_id_unique'], 
            data_object = data_object
            )
        group = mol.modifiers['MolecularNodes'].node_group
        node = nodes.add_custom_node_group_to_node(group, node_assembly.name)
        nodes.insert_last_node(group, node)
        
    
    
    return mol


def get_chain_entity_id(file):
    entities = file['entityList']
    chain_names = file['chainNameList']    
    ent_dic = {}
    for i, ent in enumerate(entities):
        for chain_idx in ent['chainIndexList']:
            chain_id = chain_names[chain_idx]
            if  chain_id in ent_dic.keys():
                next
            else:
                ent_dic[chain_id] = i
    
    return ent_dic

def set_atom_entity_id(mol, file):
    mol.add_annotation('entity_id', int)
    ent_dic = get_chain_entity_id(file)
    
    entity_ids = np.array([ent_dic[x] for x in mol.chain_id])
    
    # entity_ids = chain_entity_id[chain_ids]
    mol.set_annotation('entity_id', entity_ids)
    return entity_ids

def open_structure_rcsb(pdb_code, cache_dir = None):
    import biotite.structure.io.mmtf as mmtf
    import biotite.database.rcsb as rcsb
    
    
    file = mmtf.MMTFFile.read(rcsb.fetch(pdb_code, "mmtf", target_path = cache_dir))
    
    # returns a numpy array stack, where each array in the stack is a model in the 
    # the file. The stack will be of length = 1 if there is only one model in the file
    mol = mmtf.get_structure(file, extra_fields = ["b_factor", "charge"], include_bonds = True) 
    set_atom_entity_id(mol, file)
    return mol, file

# operator that calls the function to import the structure from the PDB
class MN_OT_Import_Protein_RCSB(bpy.types.Operator):
    bl_idname = "mn.import_protein_rcsb"
    bl_label = "import_protein_fetch_pdb"
    bl_description = "Download and open a structure from the Protein Data Bank"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        scene = context.scene
        pdb_code = scene.MN_pdb_code
        
        mol = load(
            pdb_code=pdb_code,
            centre=scene.MN_import_centre, 
            del_solvent=scene.MN_import_del_solvent,
            style=scene.MN_import_style,
            cache_dir=scene.MN_cache_dir, 
            build_assembly = scene.MN_import_build_assembly
        )
        
        bpy.context.view_layer.objects.active = mol
        self.report({'INFO'}, message=f"Imported '{pdb_code}' as {mol.name}")
        
        return {"FINISHED"}

def panel(layout_function, scene):
    col_main = layout_function.column(heading = '', align = False)
    col_main.alert = False
    col_main.enabled = True
    col_main.active = True
    col_main.use_property_split = False
    col_main.use_property_decorate = False
    col_main.scale_x = 1.0
    col_main.scale_y = 1.0
    col_main.alignment = 'Expand'.upper()
    col_main.label(text = "Download from PDB")
    col_main.prop(
        scene,
        'MN_cache_dir',
        text = 'Cache dir')
    row_import = col_main.row()
    row_import.prop(scene, 'MN_pdb_code', text='PDB ID')
    row_import.operator('mn.import_protein_rcsb', text='Download', icon='IMPORT')
    col_main.prop(scene, 'MN_import_build_assembly')