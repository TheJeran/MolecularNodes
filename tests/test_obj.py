import bpy
import numpy as np
import molecularnodes as mn
from .utils import apply_mods, get_verts, sample_attribute

def test_creat_obj():
    # Create a mesh object named "MyMesh" in the collection "MyCollection"
    # with vertex locations and bond edges.
    locations = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0]]
    bonds = [(0, 1), (1, 2), (2, 0)]
    name = "MyMesh"
    my_object = mn.blender.obj.create_object(locations, bonds, name=name)
    
    assert len(my_object.data.vertices) == 3
    assert my_object.name == name
    assert my_object.name != "name"

def test_set_position():
    mol = mn.io.pdb.load('8FAT')
    
    pos_a = sample_attribute(mol, 'position')
    
    mn.blender.obj.set_position(mol, mn.blender.obj.get_attribute(mol, 'position') + 10)

    pos_b = sample_attribute(mol, 'position')
    
    assert not np.isclose(pos_a, pos_b).all()
    assert np.isclose(pos_a, pos_b - 10, rtol = 0.001).all()