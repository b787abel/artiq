# Kasli_simple device database
core_addr = "10.179.78.14"

device_db = {
    "core": {
        "type": "local",
        "module": "artiq.coredevice.core",
        "class": "Core",
        "arguments": {"host": core_addr, "ref_period": 1e-9, "target": "rv32ima"},
    },
    "core_log": {
        "type": "controller",
        "host": "::1",
        "port": 1068,
        "command": "aqctl_corelog -p {port} --bind {bind} " + core_addr
    },
    "core_cache": {
        "type": "local",
        "module": "artiq.coredevice.cache",
        "class": "CoreCache"
    },
    "core_dma": {
        "type": "local",
        "module": "artiq.coredevice.dma",
        "class": "CoreDMA"
    },

    "i2c_switch0": {
        "type": "local",
        "module": "artiq.coredevice.i2c",
        "class": "PCA9548",
        "arguments": {"address": 0xe0}
    },
    "i2c_switch1": {
        "type": "local",
        "module": "artiq.coredevice.i2c",
        "class": "PCA9548",
        "arguments": {"address": 0xe2}
    },
}


# EEM0:
# 8 DIO channels, starting at RTIO channel 0
channel_offset = 0
for i in range(8):
    device_db["ttl" + str(i)] = {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {"channel": i},
    }
    channel_offset = channel_offset+1
    
# EEM1:
# 8 DIO channels, starting at RTIO channel 0
for i in range(8, 16):
    device_db["ttl" + str(i)] = {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {"channel": i},
    }
    channel_offset = channel_offset+1

# EEM2:
# Urukul, starting at RTIO channel 16 
device_db.update(
    eeprom_urukul2={
        "type": "local",
        "module": "artiq.coredevice.kasli_i2c",
        "class": "KasliEEPROM",
        "arguments": {"port": "EEM2"}
    },
    spi_urukul2={
        "type": "local",
        "module": "artiq.coredevice.spi2",
        "class": "SPIMaster",
        "arguments": {"channel": channel_offset}
    },
    ttl_urukul2_sync={
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLClockGen",
        "arguments": {"channel": channel_offset+1, "acc_width": 4}
    },
    ttl_urukul2_io_update={
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {"channel": channel_offset+2}
    },
    urukul2_cpld={
        "type": "local",
        "module": "artiq.coredevice.urukul",
        "class": "CPLD",
        "arguments": { #For arguments, see artiq.coredevice.urukul.CPLD init
            "spi_device": "spi_urukul2",
            "io_update_device": "ttl_urukul2_io_update",
            "sync_device": "ttl_urukul2_sync",
            "refclk": 100e6,
            "clk_sel": 0, 
            #"clk_div": 0
        }
    }
)
# number of RTIO channels used by urukul
channel_offset = channel_offset + 3

device_db.update({
    "urukul2_ch" + str(i): {
        "type": "local",
        "module": "artiq.coredevice.ad9910",
        "class": "AD9910",
        "arguments": { #For arguments, see artiq.coredevice.ad9910.AD9910 init
            "pll_n": 40,
            "pll_vco": 5,
            "chip_select": 4 + i,
            "cpld_device": "urukul2_cpld"
        }
    } for i in range(4)
})

# EEM3:
# Urukul, starting at Ch19 
device_db.update(
    eeprom_urukul3={
        "type": "local",
        "module": "artiq.coredevice.kasli_i2c",
        "class": "KasliEEPROM",
        "arguments": {"port": "EEM3"}
    },
    spi_urukul3={
        "type": "local",
        "module": "artiq.coredevice.spi2",
        "class": "SPIMaster",
        "arguments": {"channel": channel_offset}
    },
    ttl_urukul3_sync={
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLClockGen",
        "arguments": {"channel": channel_offset+1, "acc_width": 4}
    },
    ttl_urukul3_io_update={
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {"channel": channel_offset+2}
    },
    urukul3_cpld={
        "type": "local",
        "module": "artiq.coredevice.urukul",
        "class": "CPLD",
        "arguments": { #For arguments, see artiq.coredevice.urukul.CPLD init
            "spi_device": "spi_urukul3",
            "io_update_device": "ttl_urukul3_io_update",
            "sync_device": "ttl_urukul3_sync",
            "refclk": 100e6,
            "clk_sel": 0, 
            #"clk_div": 0
        }
    }
)
# number of RTIO channels used by urukul
channel_offset = channel_offset + 3

device_db.update({
    "urukul3_ch" + str(i): {
        "type": "local",
        "module": "artiq.coredevice.ad9910",
        "class": "AD9910",
        "arguments": { #For arguments, see artiq.coredevice.ad9910.AD9910 init
            "pll_n": 40,
            "pll_vco": 5,
            "chip_select": 4 + i,
            "cpld_device": "urukul3_cpld"
        }
    } for i in range(4)
})

# EEM4:
# Zotino, starting at channel 22
device_db["spi_zotino3"] = {
    "type": "local",
    "module": "artiq.coredevice.spi2",
    "class": "SPIMaster",
    "arguments": {"channel": channel_offset}
}
device_db["ttl_zotino3_ldac"] = {
    "type": "local",
    "module": "artiq.coredevice.ttl",
    "class": "TTLOut",
    "arguments": {"channel": channel_offset+1}
}
device_db["ttl_zotino3_clr"] = {
    "type": "local",
    "module": "artiq.coredevice.ttl",
    "class": "TTLOut",
    "arguments": {"channel": channel_offset+2}
}
device_db["zotino3"] = {
    "type": "local",
    "module": "artiq.coredevice.zotino",
    "class": "Zotino",
    "arguments": {
        "spi_device": "spi_zotino3",
        "ldac_device": "ttl_zotino3_ldac",
        "clr_device": "ttl_zotino3_clr"
    }
}
channel_offset = channel_offset + 3

# EEM5:
# Sampler, starting at Channel 25 
device_db["spi_sampler0_adc"] = {
    "type": "local",
    "module": "artiq.coredevice.spi2",
    "class": "SPIMaster",
    "arguments": {"channel": channel_offset}
}
device_db["spi_sampler0_pgia"] = {
    "type": "local",
    "module": "artiq.coredevice.spi2",
    "class": "SPIMaster",
    "arguments": {"channel": channel_offset+1}
}
device_db["spi_sampler0_cnv"] = {
    "type": "local",
    "module": "artiq.coredevice.ttl",
    "class": "TTLOut",
    "arguments": {"channel": channel_offset+2},
}
device_db["sampler0"] = {
    "type": "local",
    "module": "artiq.coredevice.sampler",
    "class": "Sampler",
    "arguments": {
        "spi_adc_device": "spi_sampler0_adc",
        "spi_pgia_device": "spi_sampler0_pgia",
        "cnv_device": "spi_sampler0_cnv", 
        "div": 64
    }
}
channel_offset = channel_offset + 3

# EEM6:
# Urukul, starting at Channel 28 
device_db.update(
    eeprom_urukul4={
        "type": "local",
        "module": "artiq.coredevice.kasli_i2c",
        "class": "KasliEEPROM",
        "arguments": {"port": "EEM6"}
    },
    spi_urukul4={
        "type": "local",
        "module": "artiq.coredevice.spi2",
        "class": "SPIMaster",
        "arguments": {"channel": channel_offset}
    },
    ttl_urukul4_sync={
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLClockGen",
        "arguments": {"channel": channel_offset+1, "acc_width": 4}
    },
    ttl_urukul4_io_update={
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {"channel": channel_offset+2}
    },
    urukul4_cpld={
        "type": "local",
        "module": "artiq.coredevice.urukul_mod",
        "class": "CPLD_mod",
        "arguments": { #For arguments, see artiq.coredevice.urukul.CPLD init
            "spi_device": "spi_urukul4",
            "io_update_device": "ttl_urukul4_io_update",
            "sync_device": "ttl_urukul4_sync",
            "refclk": 125e6,
            "clk_sel": 2, 
            #"clk_div": 0
        }
    }
)
# number of RTIO channels used by urukul
channel_offset = channel_offset + 3

device_db.update({
    "urukul4_ch" + str(i): {
        "type": "local",
        "module": "artiq.coredevice.ad9910_mod",
        "class": "AD9910",
        "arguments": { #For arguments, see artiq.coredevice.ad9910.AD9910 init
            "pll_n": 32,
            "pll_vco": 5,
            "chip_select": 4 + i,
            "cpld_device": "urukul4_cpld"
        }
    } for i in range(4)
})


# EEM7:
# Urukul
device_db.update(
    eeprom_urukul5={
        "type": "local",
        "module": "artiq.coredevice.kasli_i2c",
        "class": "KasliEEPROM",
        "arguments": {"port": "EEM7"}
    },
    spi_urukul5={
        "type": "local",
        "module": "artiq.coredevice.spi2",
        "class": "SPIMaster",
        "arguments": {"channel": channel_offset}
    },
    ttl_urukul5_sync={
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLClockGen",
        "arguments": {"channel": channel_offset+1, "acc_width": 4}
    },
    ttl_urukul5_io_update={
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {"channel": channel_offset+2}
    },
    urukul5_cpld={
        "type": "local",
        "module": "artiq.coredevice.urukul",
        "class": "CPLD",
        "arguments": { #For arguments, see artiq.coredevice.urukul.CPLD init
            "spi_device": "spi_urukul5",
            "io_update_device": "ttl_urukul5_io_update",
            "sync_device": "ttl_urukul5_sync",
            "refclk": 125e6,
            "clk_sel": 0, 
        }
    }
)
# number of RTIO channels used by urukul
channel_offset = channel_offset + 3

device_db.update({
    "urukul5_ch" + str(i): {
        "type": "local",
        "module": "artiq.coredevice.ad9910",
        "class": "AD9910",
        "arguments": { #For arguments, see artiq.coredevice.ad9910.AD9910 init
            "pll_n": 32,
            "pll_vco": 5,
            "chip_select": 4 + i,
            "cpld_device": "urukul5_cpld"
        }
    } for i in range(4)
})

device_db.update(
    led0={
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {"channel": channel_offset}
    },
    led1={
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {"channel": channel_offset+1}
    },
)

device_db.update(
    i2c_switch="i2c_switch0"
)

# Controllers
device_db.update(
    pyramid_camera={
            "type": "controller",
            "host": "10.179.79.17",
            "port": 10338
            },
    glass_cell_camera={
            "type": "controller",
            "host": "10.179.79.17",
            "port": 10339
            },
    scope={
            "type": "controller",
            "host": "10.179.79.17",
            "port": 10340
            },
    )

# Analog inputs
device_db.update(
        pd_cooling={
                "type": "local",
                "module": "artiq_extras.devices.samplerchannel",
                "class": "SamplerChannel",
                "arguments": {"sampler": "sampler0", "channel": 0, "gain": 0}
                })

# Memorable aliases for devices
device_db.update(
    imaging_shutter = 'ttl0',
    pyramid_shutter = "ttl1",
    glass_cell_camera_trigger = "ttl2",
    repumper_shutter = "ttl3",
    pyramid_camera_trigger = "ttl4",
    cell_shutter = 'ttl5',
    scope_trigger= 'ttl6',
    ttl_test = 'ttl7', 

    #First Urukul 
    master_detuning_aom = "urukul2_ch0",
    pyramid_cooling_detuning_aom = "urukul2_ch1",
    cell_cooling_detuning_aom = "urukul2_ch2",
    
    
    #Second Urukul
    repumper_detuning_aom = 'urukul3_ch0',
    imaging_detuning_aom = 'urukul3_ch1', 
    repumper_shutter_aom = 'urukul3_ch2', 
    urukul3_ch3_free = 'urukul3_ch3',
   
    
    #Third Urukul 
    srf_x_dds = 'urukul4_ch0', 
    evap_x = 'urukul4_ch1', 
    mrf_primary = 'urukul4_ch2', 
    mrf_secondary = 'urukul4_ch3', 
    
    
    #Fourth Urukul 
    top_x_dds = 'urukul5_ch0', 
    top_y_dds = 'urukul5_ch1', 
    urukul5_ch2_free = 'urukul5_ch2', 
    urukul5_ch3_free = 'urukul5_ch3', 
    
)

#Raspberry Pi 
device_db.update({
    'raspberry_pi': {
            "type": "controller", 
            "host": "10.179.78.16", 
            "port": 3249},
                })


