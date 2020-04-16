# MIT License
#
# Copyright (c) 2020 Archis Joglekar
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import json

import xarray as xr
import numpy as np


class StorageManager:
    def __init__(self, xax, vax, tax, base_path):
        self.base_path = base_path
        self.efield_path = os.path.join(base_path, "electric_field_vs_time.nc")
        self.driver_efield_path = os.path.join(
            base_path, "driver_electric_field_vs_time.nc"
        )
        self.f_path = os.path.join(base_path, "dist_func_vs_time.nc")

        self.__init_electric_field_storage(tax=tax, xax=xax)
        self.__init_dist_func_storage(tax=tax, xax=xax, vax=vax)

    def close(self):
        self.efield_arr.to_netcdf(self.efield_path)
        self.driver_efield_arr.to_netcdf(self.driver_efield_path)
        self.f_arr.to_netcdf(self.f_path)

    def __init_electric_field_storage(self, tax, xax):
        """
        Initialize electric field storage DataArray

        :param tax:
        :param xax:
        :param path:
        :return:
        """

        electric_field_store = np.zeros((tax.size, xax.size))

        ef_DA = xr.DataArray(
            data=electric_field_store, coords=[("time", tax), ("space", xax)]
        )

        ef_DA.to_netcdf(self.efield_path)

        self.efield_arr = xr.open_dataarray(self.efield_path)

        driver_electric_field_store = np.zeros((tax.size, xax.size))

        driver_ef_DA = xr.DataArray(
            data=driver_electric_field_store, coords=[("time", tax), ("space", xax)]
        )

        driver_ef_DA.to_netcdf(self.driver_efield_path)

        self.driver_efield_arr = xr.open_dataarray(self.driver_efield_path)

    def __init_dist_func_storage(self, tax, xax, vax):
        """
        Initialize distribution function storage

        :param tax:
        :param xax:
        :param vax:
        :param path:
        :return:
        """
        dist_func_store = np.zeros((tax.size, xax.size, vax.size))

        f_DA = xr.DataArray(
            data=dist_func_store,
            coords=[("time", tax), ("space", xax), ("velocity", vax)],
        )

        f_DA.to_netcdf(self.f_path)

        self.f_arr = xr.open_dataarray(self.f_path)

    def batched_write_to_file(self, t_range, e, e_driver, f):
        """
        Write batched to file

        This is to save time by keeping some of the history on
        accelerator rather than passing it back every time step


        :param t_range:
        :param e:
        :param e_driver:
        :param f:
        :return:
        """
        t_xr = xr.DataArray(data=t_range, dims=["time"])

        self.efield_arr.loc[t_xr, :] = e
        self.driver_efield_arr.loc[t_xr, :] = e_driver
        self.f_arr.loc[t_xr, :] = f

        # Save and reopen
        self.efield_arr.to_netcdf(self.efield_path)
        self.driver_efield_arr.to_netcdf(self.driver_efield_path)
        self.f_arr.to_netcdf(self.f_path)

        self.efield_arr = xr.open_dataarray(self.efield_path)
        self.driver_efield_arr = xr.open_dataarray(self.driver_efield_path)
        self.f_arr = xr.open_dataarray(self.f_path)

    def write_parameters_to_file(self, param_dict, filename):
        with open(os.path.join(self.base_path, filename + ".txt"), "w") as fi:
            json.dump(param_dict, fi)
