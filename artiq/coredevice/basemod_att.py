from artiq.language.core import kernel, delay
from artiq.language.units import us, ms
from artiq.coredevice.shiftreg import ShiftReg


class BaseModAtt:
    def __init__(self, dmgr, rst_n, clk, le, mosi, miso):
        self.rst_n = dmgr.get(rst_n)
        self.shift_reg = ShiftReg(dmgr,
            clk=clk, ser=mosi, latch=le, ser_in=miso, n=8*4)

    @kernel
    def reset(self):
        # HMC's incompetence in digital design an interfaces means that
        # the HMC542 needs a level low on RST_N and then a rising edge
        # on Latch Enable. Their "latch" isn't a latch but a DFF.
        # Of course, it also powers up with a random attenuation, and
        # that cannot be fixed with simple pull-ups/pull-downs.
        self.rst_n.off()
        self.shift_reg.latch.off()
        delay(1*us)
        self.shift_reg.latch.on()
        delay(1*us)
        self.shift_reg.latch.off()
        self.rst_n.on()
        delay(1*us)

    @kernel
    def set_mu(self, att0, att1, att2, att3):
        word = (
            (att0 <<  2) |
            (att1 << 10) | 
            (att2 << 18) | 
            (att3 << 26)
        )
        self.shift_reg.set(word)

    @kernel
    def get_mu(self):
        word = self.shift_reg.get()
        att0 = (word >>  2) & 0x3f
        att1 = (word >> 10) & 0x3f
        att2 = (word >> 18) & 0x3f
        att3 = (word >> 26) & 0x3f
        return att0, att1, att2, att3
