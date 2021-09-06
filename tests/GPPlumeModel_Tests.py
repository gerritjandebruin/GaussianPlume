import importlib 
from io import StringIO
import pathlib
import numpy
import pandas
import unittest
from unittest.mock import patch
import warnings



import GPImportData as GPID
import GPPlumeModel as GPPM
import GPLocationGeometry as GPLG
import GPSource as GPSO

importlib.reload(GPID)
importlib.reload(GPPM)
importlib.reload(GPLG)
importlib.reload(GPSO)



class Test_basic(unittest.TestCase):

    def setUp(self):
        self.verbose = 1
        
    def test_basic(self):
        """
        Most basic functionality. 

        """
        P = GPPM.Plume(verbose = 0)
        
    def test_stability_setter_getter(self):
        
        stability_index = numpy.array([4,3,1])
        
        P = GPPM.Plume(verbose = 0, stability_index = stability_index)
        
        print(P.stability_class)
        

class Test_calculate_concentration_prepare(unittest.TestCase):

    def setUp(self):
        self.verbose = 1
        
    def test_basic_dxdy(self):
        """
        Most basic functionality. 

        """
        data = {
            "dx": numpy.array([-296.06762177, -49.9696837]),
            "dy": numpy.array([-412.86479599, -505.58521254]),
        }
        
        df = pandas.DataFrame(data = data)
        
        P = GPPM.Plume(verbose = 0, df = df)
                
        P.calculate_concentration_prepare_dxdy()
        
        test_dx = [-296.06762177, -49.9696837]
        test_dy = [-412.86479599, -505.58521254]

        self.assertTrue(numpy.allclose(P.df["dx"].to_numpy(), test_dx))
        self.assertTrue(numpy.allclose(P.df["dy"].to_numpy(), test_dy))
        

    def test_basic_dxdy_calculate(self):
        """
        Most basic functionality. 

        """
        data = {
            "latS": numpy.array([53.2835, 53.2835]),
            "lonS": numpy.array([6.3039, 6.3039]),
            "latM": numpy.array([53.2876717, 53.2876717]),
            "lonM": numpy.array([6.3007517, 6.3007517]),
            "latR": numpy.array([53.28375, 53.28375]),
            "lonR": numpy.array([6.3024917, 6.3024917]),     
            "wind_direction": numpy.array([30,60]),
        }
        
        df = pandas.DataFrame(data = data)
        
        P = GPPM.Plume(verbose = 0, df = df)
                
        P.calculate_concentration_prepare_dxdy()
        
        test_dx = [-296.06762177, -49.9696837]
        test_dy = [-412.86479599, -505.58521254]

        self.assertTrue(numpy.allclose(P.df["dx"].to_numpy(), test_dx))
        self.assertTrue(numpy.allclose(P.df["dy"].to_numpy(), test_dy))
        


    def test_basic_dxdy_missing_column(self):
        """
        Most basic functionality. 

        """
        data = {
            "latS": numpy.array([53.2835, 53.2835]),
            "lonS": numpy.array([6.3039, 6.3039]),
            "latM": numpy.array([53.2876717, 53.2876717]),
            "lonM": numpy.array([6.3007517, 6.3007517]),
            "latR": numpy.array([53.28375, 53.28375]),
            "lonR": numpy.array([6.3024917, 6.3024917]),     
        }
        
        df = pandas.DataFrame(data = data)
        
        P = GPPM.Plume(verbose = 0, df = df)
        
        test_string = "GPPlumeModel.calculate_concentration_prepare_dxdy(): dx is missing and can not be calculated."
        with self.assertRaises(ValueError) as cm:
            with patch('sys.stdout', new_callable = StringIO) as mock_stdout:
                P.calculate_concentration_prepare_dxdy()
            self.assertTrue(mock_stdout.getvalue() == test_string)       


    def test_basic_tc(self):
        """
        Most basic functionality. 

        """
        data = {
            "tc": numpy.array([100, 200]),
            
        }
        
        df = pandas.DataFrame(data = data)
        
        P = GPPM.Plume(verbose = 0, df = df)
                
        P.calculate_concentration_prepare_tc()

        
        test_tc = numpy.array([100, 200])
        
        self.assertTrue(numpy.allclose(P.df["tc"].to_numpy(), test_tc))
        

    def test_basic_tc_calculate(self):
        """
        Most basic functionality. 

        """
        data = {
            "dx": numpy.array([296.06762177, 49.9696837]),
            "wind_speed": numpy.array([10, 20]),
        }
        df = pandas.DataFrame(data = data)
        P = GPPM.Plume(verbose = 0, df = df)
        P.calculate_concentration_prepare_tc()
        test_tc = numpy.array([0.0082241, 0.00069402])
        self.assertTrue(numpy.allclose(P.df["tc"].to_numpy(), test_tc))

    def test_calculate_concentration_prepare_dispersion_constants(self):
        """
        Most basic functionality. 

        """
        dc = numpy.array([[0.1, 0.2], [0.3, 0.4]]),
        P = GPPM.Plume(verbose = 0, dispersion_constants = dc)
        P.calculate_concentration_prepare_dispersion_constants()
        test_dc = numpy.array([[0.1, 0.2], [0.3, 0.4]])
        self.assertTrue(numpy.allclose(P.dispersion_constants, test_dc))


    def test_calculate_concentration_prepare_dispersion_constants_get(self):
        """
        Most basic functionality. 

        """
        mode = "nogepa"
        P = GPPM.Plume(verbose = 0, mode = mode)
        P.calculate_concentration_prepare_dispersion_constants()
        
        dispersion = numpy.array([
            [1.36,  0.866, 0.23, 0.85],
            [0.768, 0.897, 0.22, 0.8],
            [0.47,  0.907, 0.2,  0.76],
            [0.359, 0.902, 0.15, 0.73],
            [0.238, 0.902, 0.12, 0.67],
            [0.2,   0.902, 0.1,  0.62],
        ])
        
        self.assertTrue(numpy.allclose(P.dispersion_constants, dispersion))

    def test_calculate_concentration_get_molecular_properties(self):
        """
        Most basic functionality. 

        """
        molecules = ["no", "xyz"]
        molecular_mass = [123, 456]
        P = GPPM.Plume(verbose = 0, molecules = molecules, molecular_mass = molecular_mass)
        P.calculate_concentration_get_molecular_properties()
        self.assertTrue(numpy.allclose(P.molecular_mass, molecular_mass))
        self.assertIsNone(P.molecular_properties)
        
        
    def test_calculate_concentration_get_molecular_properties_get(self):
        """
        Most basic functionality. 

        """
        molecules = ["no"]
        molecular_mass = [30]
        P = GPPM.Plume(verbose = 0, molecules = molecules)
        P.calculate_concentration_get_molecular_properties()
        self.assertTrue(numpy.allclose(P.molecular_mass, molecular_mass))        
        self.assertIsNotNone(P.molecular_properties)


class Test_parse_location_data(unittest.TestCase):

    def setUp(self):
        self.verbose = 1

    def test_basic(self):
        
        P = GPPM.Plume(verbose = 0)


    def test_dx_dy_set_during_init(self):
    
        P = GPPM.Plume(verbose = 0, dx = 1, dy = 2)
        log = P.parse_data_location_helper()

        self.assertTrue(log['dx source'] == 'init/earlier')
        self.assertTrue(log['dy source'] == 'init/earlier')

    def test_locations_during_init(self):
        locM = GPLG.Location(1,2)
        locS = GPLG.Location(3,4)
        sources = [GPSO.Source(source_identifier = 0, molecules = "ch4", locS = locS)]
        locR = GPLG.Location(5,6)
        
        P = GPPM.Plume(verbose = 0, locM = locM, locR = locR, sources = sources)
        log = P.parse_data_location_helper()
        
        log_test = {'dx source': 'init/earlier', 'dy source': 'init/earlier', 'locR source': 'init/earlier', 'locR (lat, lon)': (5, 6), 'locM source': 'init/earlier', 'locM (lat, lon)': (1, 2), 'locS source':'locS is None'}
        
        for k, v in log_test.items():
            self.assertEqual(v, log[k])

        
    def test_locM_as_function_argument(self):
        locM1 = GPLG.Location(21,22)
        locM2 = GPLG.Location(1,2)
        locS = GPLG.Location(3,4)
        sources = [GPSO.Source(source_identifier = 0, molecules = "ch4", locS = locS)]
        locR = GPLG.Location(5,6)
        
        P = GPPM.Plume(verbose = 0, locR = locR, sources = sources, locM = locM1)
        log = P.parse_data_location_helper(locM = locM2)
        
        log_test = {
            'dx source': 'init/earlier', 
            'dy source': 'init/earlier', 
            'locR source': 'init/earlier', 
            'locR (lat, lon)': (5, 6), 
            'locM source': 'function parameter', 
            'locM (lat, lon)': (1, 2), 
            'locS source': 'locS is None'
        }

        for k, v in log_test.items():
            self.assertEqual(v, log[k]) 


    def test_locM_in_static_df_lat_lon(self):
        
        locS = GPLG.Location(3,4)
        sources = [GPSO.Source(source_identifier = 0, molecules = "ch4", locS = locS)]
        locR = GPLG.Location(5,6)
        
        df = {  
            "locM lat": [1],
            "locM lon": [2],
            "fiets": ["aap"],
        }
        
        df_static = pandas.DataFrame(df)
        
        P = GPPM.Plume(verbose = 0, locR = locR, sources = sources)
        P.df_static = df_static
        log = P.parse_data_location_helper() 
        # print(log)
        log_test = {
            'dx source': 'init/earlier', 
            'dy source': 'init/earlier', 
            'locR source': 'init/earlier', 
            'locR (lat, lon)': (5, 6), 
            'locM source': 'self.df_static lat/lon', 
            'locM [0] (lat, lon)': (1, 2), 
            'locS source': 'locS is None'
        }

        for k, v in log_test.items():
            self.assertEqual(v, log[k])  

    def test_locSX_in_static_df_lat_lon(self):
        
        locM = GPLG.Location(1,2)
        sources = [GPSO.Source(source_identifier = 0, molecules = "ch4")]
        locR = GPLG.Location(5,6)
        
        df = {  
            "locS0 lat": [3],
            "locS0 lon": [4],
            "fiets": ["aap"],
        }
        
        df_static = pandas.DataFrame(df)
        
        P = GPPM.Plume(verbose = 0, locR = locR, sources = sources, locM = locM)
        P.df_static = df_static
        log = P.parse_data_location_helper() 
        # print(log)
        log_test = {'dx source': 'init/earlier', 'dy source': 'init/earlier', 'locR source': 'init/earlier', 'locR (lat, lon)': (5, 6), 'locM source': 'init/earlier', 'locM (lat, lon)': (1, 2), 'locS source': 'locS is None', 'locS0 source': 'self.df_static lat/lon'}


        for k, v in log_test.items():
            self.assertEqual(v, log[k])  
        

    def test_locSX_from_locS(self):
        
        locM = GPLG.Location(1,2)
        locS = GPLG.Location(3,4)
        sources = [GPSO.Source(source_identifier = 0, molecules = "ch4")]
        locR = GPLG.Location(5,6)

        P = GPPM.Plume(verbose = 0, locR = locR, sources = sources, locM = locM, locS = locS)

        log = P.parse_data_location_helper() 
        # print(log)
        log_test = {'dx source': 'init/earlier', 'dy source': 'init/earlier', 'locR source': 'init/earlier', 'locR (lat, lon)': (5, 6), 'locM source': 'init/earlier', 'locM (lat, lon)': (1, 2), 'locS source': 'init/earlier', 'locS0 source': 'self.locS'}


        for k, v in log_test.items():
            self.assertEqual(v, log[k])          
        
        
        
if __name__ == '__main__': 
    verbosity = 1
       
    # if 1:
        # suite = unittest.TestLoader().loadTestsFromTestCase( Test_basic )
        # unittest.TextTestRunner(verbosity=verbosity).run(suite)    


    # if 1:
        # suite = unittest.TestLoader().loadTestsFromTestCase( Test_calculate_concentration_prepare )
        # unittest.TextTestRunner(verbosity=verbosity).run(suite)            


    if 1:
        suite = unittest.TestLoader().loadTestsFromTestCase( Test_parse_location_data )
        unittest.TextTestRunner(verbosity=verbosity).run(suite)      