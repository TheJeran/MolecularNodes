import molecularnodes as mn
import numpy as np

import random
from .constants import test_data_directory
from .utils import sample_attribute_to_string



def test_ss_id_to_numeric():
    examples = ['TURN_TY1_P68', 'BEND64', 'HELX_LH_PP_P9', 'STRN44']
    assert [3, 3, 1, 2] == [mn.io.local.ss_id_to_numeric(x) for x in examples]

def test_get_ss_from_mmcif(snapshot):
    mol, file = mn.io.local.open_structure_local_pdbx(test_data_directory / '1cd3.cif')
    mol2, fil2 = mn.io.pdb.open_structure_rcsb('1cd3')
    
    random.seed(6)
    random_idx = random.sample(range(mol.array_length()), 100)
    
    # assert (mol.sec_struct == mol2.sec_struct)[random_idx].all()
    
    snapshot.assert_match(
        np.array2string(mol.sec_struct[random_idx], precision = 3, threshold = 1e4), 
        "sec_struc.txt"
    )