
# -*- coding: utf-8 -*-


__all__ = [
		"arc_ocean_mask",
		"area_weighted_mean",
		"save_data_hdf5",
		]


from .. import np, h5py
from .. import ocean_mask_1d, ocean_mask_hd, ocean_mask_qd






def arc_ocean_mask(instrument):
    """
    Input: "CERES" or "MISR" or "MERRA"
    Get Arctic Ocean mask based on ftp://daac.ornl.gov/data/islscp_ii/ancillary/combined_ancillary_xdeg/data/
    Return the arctic ocean mask (20 * 360) array. Mask out the land grids.
    """

    raw_data = np.loadtxt(ocean_mask_1d)
    
    if instrument == 'CERES':
        # select Arctic part
        # because CERES ranges from 70.5 -> 89.5 N (20 points)
        arctic_0 = raw_data[1:21, :]
        # transform to CERES format
        # transform latitude, as CERES lat 70 -> 90 N
        arctic_1 = arctic_0[::-1]
        # transform longitude, as CERES lon 0.5 -> 359.5 E
        arctic_2 = np.array([np.append(arctic_1[i, 180:], arctic_1[i, :180]) for i in range(20)])
        m = np.ma.masked_equal(arctic_2, 1)
        
    elif instrument == 'MISR':
        # select Arctic part
        # because CERES ranges from 70.5 -> 89.5 N (20 points)
        arctic_0 = raw_data[1:21, :]
        # transform to MISR format
        # transform latitude, as MISR lat 70 -> 90 N
        arctic_1 = arctic_0[::-1]
        m = np.ma.masked_equal(arctic_1, 1)
        
    elif instrument == 'MERRA': # same as ERA-Interim
        arctic_0 = raw_data[:21, :]
        # keep it
        m = np.ma.masked_equal(arctic_0, 1)
        
    elif instrument == 'CFSR':
        raw_data = np.loadtxt(cean_mask_hd)
        # select Arctic part
        arctic_0 = raw_data[:41, :]     
        # transform longitude to 0 -> 359.5 E
        arctic_1 = np.array([np.append(arctic_0[i, 360:], arctic_0[i, :360]) for i in range(41)])
        m = np.ma.masked_equal(arctic_1, 1)
    
    elif instrument == 'JRA55':
        # convert 0.25 deg ocean mask to 1.25 deg
        raw_data = np.loadtxt(ocean_mask_qd)
        # select Arctic part
        arctic_0 = raw_data[:86, :]
        
        tmp_mask = [[] for i in range(17)]    
        for ilat in range(17):
            for ilon in range(288):
                tmp = arctic_0[ilat*5:ilat*5+5, ilon*5:ilon*5+5]
                if any(tmp.ravel() == 1):
                    tmp_mask[ilat].append(1)
                else:
                    tmp_mask[ilat].append(0)   
        arctic_0 = np.array(tmp_mask)
        # transform longitude to 0 -> 359.5 E
        arctic_1 = np.array([np.append(arctic_0[i, 144:], arctic_0[i, :144]) for i in range(17)])
        m = np.ma.masked_equal(arctic_1, 1)
        
    return m


def area_weighted_mean(data, lat):
    """
    Function used to calculate area-weighted Arctic mean value. 
    Write this function because different datasets may have different shapes. 
    This function then serves as an universal function.
    Data should be a 2-D array while lat should be a 1-D array, 
    and they should share the same first dimension.
    """

    lat_mean_data = np.nanmean(data, axis=1)
    lat_new = []
    for ilat, idata in zip(lat, lat_mean_data):
        if np.isnan(idata) == False:
            lat_new.append(ilat)
        else:
            lat_new.append(np.nan)
    area_mean = np.nansum(lat_mean_data*np.cos(np.deg2rad(lat))) / np.nansum(np.cos(np.deg2rad(lat)))
    
    return area_mean


def save_data_hdf5(filename, data_path, data):
    """
    Inputs are filename, data_path, and data
    """

    with h5py.File(filename, 'a') as h5f:
        h5f.create_dataset(data_path, data=data, compression='gzip', compression_opt=5)
    return
