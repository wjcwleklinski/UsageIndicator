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


def main():
    indicator = appindicator.Indicator.new(APPINDICATOR_ID,
                                           os.getcwd() + "/icons/chip.png",
                                           appindicator.IndicatorCategory.SYSTEM_SERVICES)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    print(os.getcwd())
    attributes = get_usage_data()
    menu, items = build_menu(attributes)
    indicator.set_menu(menu)
    indicator.set_label(attributes[len(attributes) - 1], "")
    glib.timeout_add(2000, change_labels, indicator, items)
    gtk.main()


def build_menu(attributes):
    menu = gtk.Menu()
    items =[]
    for i in range(0, len(attributes) - 1):
        new_item = gtk.MenuItem()
        new_item.set_label(str(attributes[i]))
        menu.append(new_item)
        items.append(new_item)

    item_quit = gtk.MenuItem('Quit')
    item_quit.connect('activate', quit)
    menu.append(item_quit)
    menu.show_all()
    return menu, items


def get_usage_data():
    cpu = psutil.cpu_percent(interval=1.0)
    cpu = str(cpu) + ' %'
    cpu_text = 'CPU: ' + cpu
    ram = round(psutil.virtual_memory().free / 1073741824, 2)
    ram = 'RAM: ' + str(ram) + ' GB'
    disk = round(psutil.disk_usage('/home').free / 1073741824, 2)
    disk = 'HDD: ' + str(disk) + ' GB'
    temperature = psutil.sensors_temperatures().get('coretemp')[0]
    temp = re.findall(r'\d+', str(temperature))
    final_temperature = 'Temp: ' + temp[1] + ' °C'
    attributes = [cpu_text, ram, disk, final_temperature, cpu]
    return attributes


def change_labels(indicator, items):
    attributes = get_usage_data()
    indicator.set_label(attributes[len(attributes) - 1], "")
    for i in range(0, len(items)):
        items[i].set_label(str(attributes[i]))

    return True


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()
