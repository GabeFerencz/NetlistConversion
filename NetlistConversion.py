#!/usr/bin/env python
# Gabe Ferencz
import time
import textwrap

class Netlist(object):
    def __init__(self):
        self.parts = dict()
        self.nets = dict()

    def parse_allegro(self, filename):
        # A comma denotes a continued line, so let's join those lines
        self.netlist = open(filename,'U').read().replace(',\n',' ')
        childClass = None
        for line in self.netlist.split('\n'):
            if line.startswith('$PINS') or line.startswith('$A_PROPERTIES'):
                childClass = None
            elif line.startswith('$NETS'):
                print('Parsing nets...')
                childClass = Net
            elif line.startswith('$PACKAGES'):
                print('Parsing packages...')
                childClass = Part
            elif line == '':
                pass
            else:
                if childClass is not None:
                    childClass.parse_allegro(line, self)

    def pads_output(self, filename):
        outputData = '!PADS-POWERPCB-V3.0-MILS !Pads Power PCB Converted file '
        outputData += time.strftime('%Y-%b-%d %H-%M')
        outputData += '\n\n*PART*\n\n' + \
                ''.join([part.pads_format() for part in self.parts.values()])
        outputData += '\n\n*NET*\n\n' + \
                ''.join([net.pads_format() for net in self.nets.values()])

        outfile = open(filename, 'w')
        outfile.write(outputData)
        outfile.close()

class Part(object):
    def __init__(self, refDes = '', footprint = '', partNumber = '',
                        value = '', tolerance = ''):
        self.footprint = footprint
        self.partNumber = partNumber
        self.value = value
        self.tolerance = tolerance
        self.refDes = refDes

    def __repr__(self):
        return self.refDes

    def pads_format(self):
        return self.refDes + ' ' + self.partNumber + '\n'

    @staticmethod
    def parse_allegro(line, parent):
        # sample:
        # 'IPC_RES_SMT_0603H1P2' ! '803Wxxxxx' ! '75' ! '  1%' ;  R61 R60
        details = line.split(' ; ')[0].split(' ! ')
        details = [detail.strip("'") for detail in details]
        # A single line defines one or more instances of a part
        instances = line.split(' ; ')[1].split()
        for instance in instances:
            parent.parts.update({instance:Part(instance,*details)})

class Net(object):
    def __init__(self,netName,nodes):
        self.netName = netName
        self.nodes = nodes.split()
        pass

    def __repr__(self):
        return self.netName

    def pads_format(self):
        return '*signal* '+self.netName + '\n' + \
                textwrap.fill(' '.join(self.nodes),79) + '\n\n'

    @staticmethod
    def parse_allegro(line, parent):
        # sample:
        # 'CONFIG_OUT' ; R7.2 R76.1 R83.2 U1.78
        netName = line.split(' ; ')[0].strip("'")
        nodes = line.split(' ; ')[1]
        parent.nets.update({netName:Net(netName,nodes)})

if __name__ == "__main__":
    import sys
    filenames = sys.argv[1:]
    for filename in filenames:
        print(filename)
        if filename.endswith('.tel'):
            netlist = Netlist()
            netlist.parse_allegro(filename)
            netlist.pads_output(filename[:-4]+'_Pads.asc')
    print('Conversion complete...')