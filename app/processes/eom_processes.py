from datetime import datetime
import logging

sentinel2_l1c_start_date = datetime(2015, 7, 1).date()

landsat45_l1_start_date = datetime(1984, 4, 1).date()
landsat45_l1_end_date = datetime(2012, 6, 1).date()

landsat8_l1_start_date = datetime(2013, 3, 1).date()

sh_waterbodies_start_date = datetime(2020, 10, 1).date()

st_ppi_start_date = datetime(2017, 1, 1).date()

sh_vpp_start_date = datetime(2017, 1, 1).date()

daily__start_date = datetime(2022, 7, 1).date()

def create_instrument(name, processing_module, start, end):
    return {
        'name': name,
        'args' : {
            'instrument': name,
            'processing_module': processing_module
        },
        'start': start,
        'end': end
    }

eom_processes = [
    # 10 DAILY
    # {
    #    'name': 'st-ppi', # check if renaming to st_ppi works?
    #    'frequency': '10D',
    #    'instruments': [{
    #        'name': 'copernicus_services',
    #        'args' : {
    #            'instrument': 'copernicus_services',
    #            'processing_module': 'st-ppi'
    #        },
    #        'start': st_ppi_start_date,
    #        'end': None
    #    }]
    # },
    
    # MONTHLY
    {
        'name': 'barren_soil', # No LANDSAT script so can only go back to start of S2
        'frequency': 'monthly',
        'instruments': [{
            'name': 'sentinel2_l1c',
            'args' : {
                'instrument': 'sentinel2_l1c',
                'processing_module': 'barren_soil'
            },
            'start': sentinel2_l1c_start_date,
            'end': None
        }]
    },
    {
        'name': 'ndmi_special', # ready for run
        'frequency': 'monthly',
        'instruments': [{
            'name': 'sentinel2_l1c',
            'args' : {
                'instrument': 'sentinel2_l1c',
                'processing_module': 'ndmi'
            },
            'start': sentinel2_l1c_start_date,
            'end': None
        },{
            'name': 'landsat45_l1',
            'args' : {
                'instrument': 'landsat_tm_l1',
                'processing_module': 'ndmi'
            },
            'start': landsat45_l1_start_date,
            'end': landsat45_l1_end_date
        }]
    },
    {
        'name': 'ndvi', # ready for run
        'frequency': 'monthly',
        'instruments': [{
            'name': 'sentinel2_l1c',
            'args' : {
                'instrument': 'sentinel2_l1c',
                'processing_module': 'ndvi'
            },
            'start': sentinel2_l1c_start_date,
            'end': None
        }, {
            'name': 'landsat45_l1',
            'args' : {
                'instrument': 'landsat_tm_l1',
                'processing_module': 'ndvi'
            },
            'start': landsat45_l1_start_date,
            'end': landsat45_l1_end_date
        }]
    },
    {
        'name': 'ndwi', # ready for run
        'frequency': 'monthly',
        'instruments': [{
            'name': 'sentinel2_l1c',
            'args' : {
                'instrument': 'sentinel2_l1c',
                'processing_module': 'ndwi'
            },
            'start': sentinel2_l1c_start_date,
            'end': None
        }, {
            'name': 'landsat45_l1',
            'args' : {
                'instrument': 'landsat_tm_l1',
                'processing_module': 'ndwi'
            },
            'start': landsat45_l1_start_date,
            'end': landsat45_l1_end_date
        }]
    },
    {
        'name': 'true_color', # ready for run (note american spelling for processing_module)
        'frequency': 'monthly',
        'instruments': [{
            'name': 'sentinel2_l2a',
            'args' : {
                'instrument': 'sentinel2_l2a',
                'processing_module': 'true_color'
            },
            'start': sentinel2_l1c_start_date,
            'end': None
        }, {
            'name': 'landsat45_l2',
            'args' : {
                'instrument': 'landsat_tm_l2',
                'processing_module': 'true-color'
            },
            'start': landsat45_l1_start_date,
            'end': landsat45_l1_end_date
        }]
    },    
    {
        'name': 'water_bodies', # ready for run
        'frequency': 'monthly',
        'instruments': [{
            'name': 'copernicus_services',
            'args' : {
                'instrument': 'copernicus_services',
                'processing_module': 'water-bodies'
            },
            'start': sh_waterbodies_start_date,
            'end': None
        }]
    },    
    {
        'name': 'water_bodies_occurence', # ready for run
        'frequency': 'monthly',
        'instruments': [{
            'name': 'copernicus_services',
            'args' : {
                'instrument': 'copernicus_services',
                'processing_module': 'water-bodies-occurence'
            },
            'start': sh_waterbodies_start_date,
            'end': None
        }]
    },    
    {
        'name': 'water_in_wetlands_index', # testing needed
        'frequency': 'monthly',
        'instruments': [{
        #    'name': 'landsat8_l2',
        #    'args' : {
        #        'instrument': 'landsat_ot_l2',
        #        'processing_module': 'wiw_L8_script'
        #    },
        #    'start': landsat8_l1_start_date,
        #    'end': sentinel2_l1c_start_date
        #},
        #{
            'name': 'sentinel2_l1c',
            'args' : {
                'instrument': 'sentinel2_l1c',
                'processing_module': 'wiw_s2_script'
            },
            'start': sentinel2_l1c_start_date,
            'end': None
        }]
    },

    #DAILY
    {
        'name': 'sar_false_color_visualization', # No LANDSAT script so can only go back to start of S2
        'frequency': 'daily',
        'instruments': [{
            'name': 'SENTINEL1_IW',
            'args' : {
                'instrument': 'SENTINEL1_IW',
                'processing_module': 'sar_false_color_visualization'
            },
            'start': daily__start_date,
            'end': None
        }]
    },
    {
        'name': 'barren_soil', # No LANDSAT script so can only go back to start of S2
        'frequency': 'daily',
        'instruments': [{
            'name': 'sentinel2_l2a',
            'args' : {
                'instrument': 'sentinel2_l2a',
                'processing_module': 'barren_soil'
            },
            'start': daily__start_date,
            'end': None
        }]
    },
    {
        'name': 'ndmi_special', 
        'frequency': 'daily',
        'instruments': [{
            'name': 'sentinel2_l1c',
            'args' : {
                'instrument': 'sentinel2_l1c',
                'processing_module': 'ndmi'
            },
            'start': daily__start_date,
            'end': None
        }]
    },
    {
        'name': 'ndvi', 
        'frequency': 'daily',
        'instruments': [{
            'name': 'sentinel2_l1c',
            'args' : {
                'instrument': 'sentinel2_l1c',
                'processing_module': 'ndvi'
            },
            'start': daily__start_date,
            'end': None
        }]
    },

     {
        'name': 'ndwi', 
        'frequency': 'daily',
        'instruments': [{
            'name': 'sentinel2_l1c',
            'args' : {
                'instrument': 'sentinel2_l1c',
                'processing_module': 'ndwi'
            },
            'start': daily__start_date,
            'end': None
        }]
    },

    
    # YEARLY
    {
        'name': 'global_surface_water_extent', # testing - https://collections.sentinel-hub.com/global-surface-water/ why not showing from 1984?
        'frequency': 'yearly',
        'instruments': [{
            'name': 'copernicus_services',
            'args' : {
                'instrument': 'copernicus_services',
                'processing_module': 'global_surface_water_extent'
            },
            'start': datetime(2019, 1, 1).date(), #landsat45_l1_start_date
            'end': None
        }]
    },
    {
        'name': 'global_surface_water_occurrence', # testing - https://collections.sentinel-hub.com/global-surface-water/ why not showing from 1984?
        'frequency': 'yearly',
        'instruments': [{
            'name': 'copernicus_services',
            'args' : {
                'instrument': 'copernicus_services',
                'processing_module': 'global_surface_water_occurrence'
            },
            'start': datetime(2019, 1, 1).date(), #landsat45_l1_start_date
            'end': None
        }]
    },
    {
        'name': 'global_surface_water_change', # testing - https://collections.sentinel-hub.com/global-surface-water/ why not showing from 1984?
        'frequency': 'yearly',
        'instruments': [{
            'name': 'copernicus_services',
            'args' : {
                'instrument': 'copernicus_services',
                'processing_module': 'global_surface_water_change'
            },
            'start': datetime(2019, 1, 1).date(), #landsat45_l1_start_date
            'end': None
        }]
    },
    {
        'name': 'global_surface_water_recurrence', # testing - https://collections.sentinel-hub.com/global-surface-water/ why not showing from 1984?
        'frequency': 'yearly',
        'instruments': [{
            'name': 'copernicus_services',
            'args' : {
                'instrument': 'copernicus_services',
                'processing_module': 'global_surface_water_recurrence'
            },
            'start': datetime(2019, 1, 1).date(), #landsat45_l1_start_date
            'end': None
        }]
    },
    {
        'name': 'global_surface_water_seasonality', # testing - https://collections.sentinel-hub.com/global-surface-water/ why not showing from 1984?
        'frequency': 'yearly',
        'instruments': [{
            'name': 'copernicus_services',
            'args' : {
                'instrument': 'copernicus_services',
                'processing_module': 'global_surface_water_seasonality'
            },
            'start': datetime(2019, 1, 1).date(), #landsat45_l1_start_date
            'end': None
        }]
    },
    {
        'name': 'global_surface_water_transitions', # testing - https://collections.sentinel-hub.com/global-surface-water/ why not showing from 1984?
        'frequency': 'yearly',
        'instruments': [{
            'name': 'copernicus_services',
            'args' : {
                'instrument': 'copernicus_services',
                'processing_module': 'global_surface_water_transitions'
            },
            'start': datetime(2019, 1, 1).date(), #landsat45_l1_start_date
            'end': None
        }]
    },
    {
        'name': 'vpp-total-productivity-tprod', # check if renaming to vpp_total_productivity_tprod works?
        'frequency': 'yearly',
        'instruments': [{
            'name': 'copernicus_services',
            'args' : {
                'instrument': 'copernicus_services',
                'processing_module': 'vpp-total-productivity-tprod'
            },
            'start': sh_vpp_start_date,
            'end': datetime(2020, 12, 31).date() #None
        }]
    },
    
    # CUSTOM
    {
        'name': 'corine_land_cover', # ready for run
        'frequency': 'yearly',
        'instruments': map(lambda year: create_instrument('copernicus_services', 'corine_land_cover', datetime(year, 1, 1).date(), datetime(year, 12, 31).date()), [1990, 2000, 2006, 2012, 2018]) 
    }
    
    # {
    #    'name': 'vpp-seasonal-productivity-sprod',
    #    'frequency': 'yearly',
    #    'instruments': [{
    #        'name': 'copernicus_services',
    #        'args' : {
    #            'instrument': 'copernicus_services',
    #            'processing_module': 'vpp-seasonal-productivity-sprod'
    #        },
    #        'start': sh_vpp_start_date, #datetime(2017, 1, 1).date(),
    #        'end': None, #datetime(2021, 12, 31).date()
    #    }]
    # },
    # {
    #    'name': 'vpp-amplitude-ampl',
    #    'frequency': 'yearly',
    #    'instruments': [{
    #        'name': 'copernicus_services',
    #        'args' : {
    #            'instrument': 'copernicus_services',
    #            'processing_module': 'vpp-amplitude-ampl'
    #        },
    #        'start': datetime(2017, 1, 1).date(),
    #        'end': datetime(2020, 12, 31).date()
    #    }]
    # },
    # {
    #    'name': 'vpp-end-of-season-value-eosv',
    #    'frequency': 'yearly',
    #    'instruments': [{
    #        'name': 'copernicus_services',
    #        'args' : {
    #            'instrument': 'copernicus_services',
    #            'processing_module': 'vpp-amplitude-ampl'
    #        },
    #        'start': datetime(2017, 1, 1).date(),
    #        'end': datetime(2020, 12, 31).date()
    #    }]
    # },
    # {
    #    'name': 'vpp-season-maximum-value-maxv',
    #    'frequency': 'yearly',
    #    'instruments': [{
    #        'name': 'copernicus_services',
    #        'args' : {
    #            'instrument': 'copernicus_services',
    #            'processing_module': 'vpp-season-maximum-value-maxv'
    #        },
    #        'start': datetime(2017, 1, 1).date(),
    #        'end': datetime(2020, 12, 31).date()
    #    }]
    # },
    # {
    #    'name': 'vpp-season-minimum-value-minv',
    #    'frequency': 'yearly',
    #    'instruments': [{
    #        'name': 'copernicus_services',
    #        'args' : {
    #            'instrument': 'copernicus_services',
    #            'processing_module': 'vpp-season-minimum-value-minv'
    #        },
    #        'start': datetime(2017, 1, 1).date(),
    #        'end': datetime(2020, 12, 31).date()
    #    }]
    # },
    # {
    #    'name': 'vpp-slope-of-greening-up-period-lslope',
    #    'frequency': 'yearly',
    #    'instruments': [{
    #        'name': 'copernicus_services',
    #        'args' : {
    #            'instrument': 'copernicus_services',
    #            'processing_module': 'vpp-slope-of-greening-up-period-lslope'
    #        },
    #        'start': datetime(2017, 1, 1).date(),
    #        'end': datetime(2020, 12, 31).date()
    #    }]
    # },
    # {
    #    'name': 'vpp-slope-of-senescent-period-rslope',
    #    'frequency': 'yearly',
    #    'instruments': [{
    #        'name': 'copernicus_services',
    #        'args' : {
    #            'instrument': 'copernicus_services',
    #            'processing_module': 'vpp-slope-of-senescent-period-rslope'
    #        },
    #        'start': datetime(2017, 1, 1).date(),
    #        'end': datetime(2020, 12, 31).date()
    #    }]
    # },
    # {
    #    'name': 'vpp-start-of-season-value-sosv',
    #    'frequency': 'yearly',
    #    'instruments': [{
    #        'name': 'copernicus_services',
    #        'args' : {
    #            'instrument': 'copernicus_services',
    #            'processing_module': 'vpp-start-of-season-value-sosv'
    #        },
    #        'start': datetime(2017, 1, 1).date(),
    #        'end': datetime(2020, 12, 31).date()
    #    }]
    # },
    
    # {
    #    'name': 'global_land_cover',
    #    'frequency': 'yearly',
    #    'instruments': [{
    #        'name': 'copernicus_services',
    #        'args' : {
    #            'instrument': 'copernicus_services',
    #            'processing_module': 'global_land_cover'
    #        },
    #        'start': datetime(2015, 1, 1).date(),
    #        'end': datetime(2019, 12, 31).date()
    #    }]
    # },
]

# logging.info('Available Processes:')
# logging.info(','.join(list(map(lambda p: p['name'], eom_processes))))