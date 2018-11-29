#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  PySmartlink.py
#
#  Copyright 2018 JONVILLE Guillaume <g.jonville@b2ei.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

import os
import pipes
import requests
import time
import typing


class Device:
    """RS485 Device"""
    Status = 0
    Address = None
    BreakerRating = 1
    IsFirmwareSupported = True
    Label = ''
    Name = ''
    Phase = '1_Phase',
    Product = None
    ResetEnergy = False
    Usage = ''

    def __init__(self, data: dict):

        if 'Status' in data:
            self.Status = data['Status']

        if 'Address' in data:
            self.Address = data['Address']
        elif 'Modbus_Slave_ID' in data:
            self.Address = data['Modbus_Slave_ID']

        if 'BreakerRating' in data:
            self.Product = data['BreakerRating']

        if 'IsFirmwareSupported' in data:
            self.Product = data['IsFirmwareSupported']

        if 'Label' in data:
            self.Label = data['Label']

        if 'Name' in data:
            self.Name = data['Name']

        if 'Phase' in data:
            self.Phase = data['Phase']

        if 'Product' in data:
            self.Product = data['Product']
        elif 'Type' in data:
            self.Product = data['Type']

        if 'ResetEnergy' in data:
            self.ResetEnergy = data['ResetEnergy']

        if 'Usage' in data:
            self.Usage = data['Usage']

    def to_array(self) -> dict:
        return {'Address': self.Address, 'BreakerRating': self.BreakerRating,
                'IsFirmwareSupported': self.IsFirmwareSupported,
                'Label': self.Label, 'Name': self.Name, 'Phase': self.Phase,
                'Product': self.Product, 'ResetEnergy': self.ResetEnergy, 'Usage': self.Usage}

    def to_string(self, prefix: str = '', suffix: str = '') -> str:
        return "%sid: %s, type: %s, name: %s, label: %s%s" % (
            prefix, self.Address, self.Product, self.Name, self.Label, suffix)


class SmartlinkDevices:
    """RS485 Device types"""
    Smartlink_RS485 = 'Smartlink RS485'
    PM3250 = 'PM3250'
    PM3255 = 'PM3255'
    iEM3150 = 'iEM3150'
    iEM3155 = 'iEM3155'
    iEM3250 = 'iEM3250'
    iEM3255 = 'iEM3255'
    iEM3350 = 'iEM3350'
    iEM3355 = 'iEM3355'


class SmartlinkResponse:
    """Smartlink responses"""
    success = 1
    error = 0
    conflict = -1


class SmartlinkEquipments:
    """Smartlink way equipments"""
    OFSD24 = 'OFSD24'
    iOFSD24 = 'iOFSD24'
    ReflexiC60 = 'ReflexiC60'
    RCAiC60 = 'RCAiC60'
    iACT24 = 'iACT24'
    iATL24 = 'iATL24'
    PM3210 = 'PM3210'
    PM3255 = 'PM3255'
    iEM3110 = 'iEM3110'
    iEM3155 = 'iEM3155'
    iEM3210 = 'iEM3210'
    iEM3255 = 'iEM3255'
    iEM3355 = 'iEM3355'
    iEM2000T = 'iEM2000T'
    Breaker_IO = 'Breaker IO'
    Pulse_Counter = 'Pulse Counter'
    Standard_Input = 'Standard Input'
    Standard_Output = 'Standard Output'


class SmartlinkUsages:
    """Smartlink usages"""
    Main_Incomer = 'Main/Incomer'
    Sub_Head_of_group = 'Sub/Head of group'
    Heating = 'Heating'
    Cooling = 'Cooling'
    HVAC = 'HVAC'
    Ventilation = 'Ventilation'
    Lighting = 'Lighting'
    Office_Equipment = 'Office Equipment'
    Cooking = 'Cooking'
    Food_Refrigeration = 'Food Refrigeration'
    Elevators = 'Elevators'
    Computers = 'Computers'
    Renewable_Energy_Production = 'Renewable Energy Production'
    Genset = 'Genset'
    Compressed_Air = 'Compressed Air'
    Vapor = 'Vapor'
    Machine = 'Machine'
    Process = 'Process'
    Water = 'Water'
    Other_Sockets = 'Other Sockets'
    Other = 'Other'


class Smartlink:
    """Smartlink main class"""
    ip = None

    username = None
    password = None

    session = None

    def __init__(self, ip: str, username: str = 'admin', password: str = 'admin'):
        self.ip = ip
        self.username = username
        self.password = password
        self.session = requests.session()

    def url(self, path: str = '/') -> str:
        return 'http://%s%s' % (self.ip, path)

    def login(self, username: str = None, password: str = None) -> int:
        if username is not None:
            self.username = username
        if password is not None:
            self.password = password
        data = self.session.get(self.url('/'))
        if data.status_code != 200: return False
        if data.text.find('login') > 0:
            data = self.session.post(self.url('/rs/login'),
                                     json={'username': self.username, 'password': self.password})
            return SmartlinkResponse.success if data.status_code == 202 else SmartlinkResponse.error
        return SmartlinkResponse.success

    def logout(self) -> int:
        data = self.session.post(self.url('/rs/logout'), {})
        return SmartlinkResponse.success if data.status_code == 202 else SmartlinkResponse.error

    def identification(self) -> typing.Union[dict, int]:
        data = self.session.get(self.url('/rs/DeviceIdentification'))
        return data.json() if data.status_code == 200 else SmartlinkResponse.error

    def change_name(self, name: str) -> int:
        identification_data = self.identification()
        identification_data['UserApplicationName'] = name
        self.session.put(self.url('/rs/DeviceIdentification'), json=identification_data)
        data = self.session.put(self.url('/slip/SmartlinkDevice'),
                                json={'Building': 'BuildingName', 'Name': name, 'ProductState': 'Nominal'})
        return SmartlinkResponse.success if data.status_code == 202 else SmartlinkResponse.error

    def add_way(self, slave_id: int, channel: int, label: str, asset_name: str, product: str = 'OFSD24', usage: str = 'Lighting', fav: bool = True) -> int:
        if slave_id >= 255:
            slave_id = 0
        data = self.session.post(self.url('/slip/DigitalChannelConfig/instances'),
                                 json={'Channel_ID': channel, 'ConfigPrm': '10', 'Energy': '0', 'IO': '1', 'IsFav': fav,
                                       'Label': label, 'Parent_ID': slave_id, 'Product': product, 'Unit': 'Wh',
                                       'Usage': usage, 'Zone': asset_name})
        if data.status_code == 200:
            return SmartlinkResponse.success
        elif data.status_code == 409:
            return SmartlinkResponse.conflict
        else:
            return SmartlinkResponse.error

    def reboot(self) -> int:
        data = self.session.post(self.url('/rs/Device/methods/Reboot'), json={})
        if data.status_code == 403:
            return SmartlinkResponse.success
        else:
            return SmartlinkResponse.error

    def is_up(self) -> int:
        return SmartlinkResponse.success if os.system("ping -c 1 " + pipes.quote(self.ip) + " > /dev/null 2>&1 ") is 0 else SmartlinkResponse.error

    def discover(self, start_id=1, stop_id=8, completion_callback=None):
        data = self.session.post(self.url('/slip/Firmware/methods/discover'),
                                 json={'Command': 1, 'Start_ID': start_id, 'Stop_ID': stop_id})
        if data.status_code == 200:
            while True:
                time.sleep(1)
                data = self.session.post(self.url('/slip/Firmware/methods/discover'),
                                         json={'Command': 2, 'Start_ID': start_id, 'Stop_ID': stop_id})
                if data.status_code == 200:
                    data = data.json()
                    if int(data['Completion']) == 100:
                        return map(lambda device: Device(device), data['DevicesDiscovered'])
                    else:
                        if callable(completion_callback):
                            completion_callback(int(data['Completion']))
                        continue
                else:
                    return SmartlinkResponse.error
        else:
            return SmartlinkResponse.error

    def get_device(self) -> typing.Union[dict, int]:
        data = self.session.get(self.url('/slip/ModbusDevice/instances'))
        if data.status_code == 200:
            return map(lambda device: Device(device), data.json())
        else:
            return SmartlinkResponse.error

    def add_raw_device(self, slave_id: int, label: str, name: str, product: str) -> int:
        data = self.session.post(self.url('/slip/ModbusDevice/instances'),
                                 json={'Address': slave_id, 'BreakerRating': 1, 'IsFirmwareSupported': True,
                                       'Label': label, 'Name': name, 'Phase': '1_Phase',
                                       'Product': product, 'ResetEnergy': 'false', 'Usage': ''})
        if data.status_code == 200:
            return SmartlinkResponse.success
        else:
            return SmartlinkResponse.error

    def add_device(self, device: Device) -> int:
        data = self.session.post(self.url('/slip/ModbusDevice/instances'), json=device.to_array())
        if data.status_code == 200:
            return SmartlinkResponse.success
        else:
            return SmartlinkResponse.error


