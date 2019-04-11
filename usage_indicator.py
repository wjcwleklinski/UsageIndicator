#!/usr/bin/env python3
import psutil
import signal
import re
import gi
import os
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import GLib as glib

APPINDICATOR_ID = 'usageindicator'
REPEAT_TIME_MS = 2000
attributes_prefix = ['CPU: ', 'RAM: ', 'HDD: ', 'Temp: ']
icons = ['/cpu.png', '/ram.png', '/hdd.png', '/temp.png']


class Indicator:

    def __init__(self, name=None, icon=None):
        self.path = os.path.abspath(os.path.dirname(__file__))

        signal.signal(signal.SIGINT, signal.SIG_DFL)

        if name is None:
            self.name = "UsageIndicator"
        else:
            self.name = name

        if icon is None:
            self.icon = gtk.STOCK_INFO
        else:
            self.icon = icon

        self.indicator = appindicator.Indicator.new(
            self.name, self.icon,
            appindicator.IndicatorCategory.SYSTEM_SERVICES
        )
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)

        usage_data = self.get_usage_data()
        menu, items = self.build_menu(usage_data)

        self.current_top_label_index = 0
        self.indicator.set_menu(menu)
        glib.timeout_add(REPEAT_TIME_MS, self.update_labels, items)

        gtk.main()

    def get_usage_data(self):
        cpu = psutil.cpu_percent(interval=1.0)
        cpu = str(cpu) + ' %'
        ram = round(psutil.virtual_memory().free / 1073741824, 2)
        ram = str(ram) + ' GB'
        disk = round(psutil.disk_usage('/home').free / 1073741824, 2)
        disk = str(disk) + ' GB'
        temperature = psutil.sensors_temperatures().get('coretemp')[0]
        temp = re.findall(r'\d+', str(temperature))
        final_temperature = temp[1] + ' °C'
        attributes = [cpu, ram, disk, final_temperature]
        return attributes

    def build_menu(self, attributes):
        menu = gtk.Menu()
        items = []
        for i in range(0, len(attributes)):

            new_item = gtk.ImageMenuItem()
            new_item.set_label(attributes_prefix[i] + str(attributes[i]))
            # every item has activate signal
            new_item.connect('activate', self.put_on_top, i)
            #

            menu.append(new_item)
            items.append(new_item)

        item_quit = gtk.MenuItem('Quit')
        item_quit.connect('activate', quit)
        menu.append(item_quit)
        menu.show_all()
        return menu, items

    def update_labels(self, items):
        attributes = self.get_usage_data()
        self.indicator.set_label(attributes[self.current_top_label_index], "")
        # update rest of menu
        for i in range(0, len(items)):
            items[i].set_label(attributes_prefix[i] + str(attributes[i]))

        return True

    def put_on_top(self, obj, index):
        self.current_top_label_index = index
        self.indicator.set_icon(self.path + '/icons' + icons[index])
        return True


if __name__ == "__main__":
    indicator = Indicator('Usage indicator', os.path.dirname(os.path.realpath(__file__)) + "/icons/cpu.png")
