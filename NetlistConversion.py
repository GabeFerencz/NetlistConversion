#!/usr/bin/env python
# Gabe Ferencz
import sys
import time

class Part(object):
    parts = dict()

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
    def parse_allegro(line):
        # sample:
        # 'IPC_RES_SMT_0603H1P2' ! '803Wxxxxx' ! '75' ! '  1%' ;  R61 R60
        details = line.split(' ; ')[0].split(' ! ')
        details = [detail.strip("'") for detail in details]
        # A single line defines one or more instances of a part
        instances = line.split(' ; ')[1].split()
        for instance in instances:
            Part.parts.update({instance:Part(instance,*details)})

    @staticmethod
    def pads_output():
        return '\n\n*PART*\n\n' + \
                ''.join([part.pads_format() for part in Part.parts.values()])

class Net(object):
    nets = dict()

    def __init__(self,netName,nodes):
        self.netName = netName
        self.nodes = nodes.split()
        pass

    def __repr__(self):
        return self.netName

    def pads_format(self):
        return '*signal* '+self.netName + '\n' + ' '.join(self.nodes) + '\n\n'

    @staticmethod
    def parse_allegro(line):
        # sample:
        # 'CONFIG_OUT' ; R7.2 R76.1 R83.2 U1.78
        netName = line.split(' ; ')[0].strip("'")
        nodes = line.split(' ; ')[1]
        return Net.nets.update({netName:Net(netName,nodes)})

    @staticmethod
    def pads_output():
        return '\n\n*NET*\n\n' + \
                ''.join([net.pads_format() for net in Net.nets.values()])

def convert_allegro_to_pads(filename):
    # A comma denotes a continued line, so let's join those lines with spaces
    netlist = open(filename,'U').read().replace(',\n',' ')
    parse_allegro(netlist)
    # Create the Pads ascii file
    outputData = '!PADS-POWERPCB-V3.0-MILS  !Pads Power PCB Converted file '
    outputData += time.strftime('%Y-%b-%d %H-%M')
    outputData += Part.pads_output()
    outputData += Net.pads_output()
    
    outfile = open(filename[:-4]+'_Pads.asc','w')
    outfile.write(outputData)
    outfile.close()

def parse_allegro(netlist):
    currClass = None
    for line in netlist.split('\n'):
        if line.startswith('$PINS') or line.startswith('$A_PROPERTIES'):
            currClass = None
        elif line.startswith('$NETS'):
            print('Parsing nets...')
            currClass = Net
        elif line.startswith('$PACKAGES'):
            print('Parsing packages...')
            currClass = Part
        elif line == '':
            pass
        else:
            if currClass is not None:
                currClass.parse_allegro(line)

if __name__ == "__main__":
    filenames = sys.argv[1:]
    for filename in filenames:
        print(filename)
        if filename.endswith('.tel'):
            convert_allegro_to_pads(filename)
    print('Conversion complete...')