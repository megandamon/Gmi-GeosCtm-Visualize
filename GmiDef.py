#------------------------------------------------------------------------------
# NASA/GSFC
#------------------------------------------------------------------------------
# AUTHORS:      Megan Damon
# AFFILIATION:  NASA GSFC / SSAI
# DATE:         May 28 2019 
#
# DESCRIPTION:
# GMI-CTM offline specific information
#------------------------------------------------------------------------------


class GmiDef:
    '''Class for keeping track of an item in inventory.'''

    GMI_IGNORE_FIELDS = ['hdf_dim', 'species_dim', 'am', 'bm', 'ai', 'bi', \
                              'pt', 'metdata_name', 'const_labels', 'const', \
                              'drydep_spc_labels', 'drydep_spc_dim', 'wetdep_spc_dim', \
                              'wetdep_spc_labels', 'emiss_spc_dim', 'emiss_spc_labels', \
                              'emiss_spc_dim2', 'emiss_spc_labels2', 'mcor']
    
    GMI_TWOD_FIELDS = ['mcor', 'psf', 'flashrate_nc', 'cldmas0_nc', 'cmi_flags1_nc', \
                           'cmi_flags_nc', 'dry_depos']
    
    GMI_QUICK_FIELDS = ['CH4', 'CO', 'HNO3', 'N2O', 'NO2', 'O3', 'OH', 'BrONO2', \
                            'HCl', 'ALK4', 'PAN', 'flashrate_nc']

    GMI_STANDARD_FIELDS = ['CH2O',    'CH4', 'CO', 'HNO3',   'HNO4', 'HO2', 'H2O2',  'MO2', \
                               'MP',      'N2O' , 'NO', 'NO2',  'NO3',    'N2O5',    'O1D', \
                               'O3',     'OH',  'BrCl',    'BrO',     'BrONO2', \
                               'HBr',     'HOBr',    'Cl2',    'ClO',     'ClONO2', \
                               'HCl', 'HOCl', 'CH3Br', 'CH3Cl', 'CFCl3', 'CF2Cl2',  'CFC113',  \
                               'HCFC22', 'CF2Br2',  'ALD2', \
                               'ALK4', 'C2H6', 'GLYX', 'PAN', 'ACET', 'flashrate_nc']
