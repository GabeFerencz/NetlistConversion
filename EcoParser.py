#!/usr/bin/env python
# Gabe Ferencz
import NetlistConversion

def parse_eco_errors(ecoErrorFile, partsDict):
    ecoErrors = open(ecoErrorFile,'U').read()
    missing = []
    invalid = []
    for line in ecoErrors.split('\n'):
        if line.startswith('* Not valid pin name '):
            invalidPart = line.split()[-1].strip()
            invalidPartNumber = partsDict[invalidPart].partNumber
            if invalidPartNumber not in invalid:
                invalid.append(invalidPartNumber)
        elif line.startswith('* Failed to get '):
            missingPart = line.split()[4]
            if missingPart not in missing:
                missing.append(missingPart)
    return invalid, missing

if __name__ == "__main__":
    import sys
    filenames = sys.argv[1:]
    for filename in filenames:
        if filename.endswith('.tel'):
            telFile = filename
        elif filename.endswith('eco.err'):
            ecoFile = filename
    netlist = NetlistConversion.Netlist()
    netlist.parse_allegro(telFile)
    invalid, missing = parse_eco_errors(ecoFile, netlist.parts)
    ofile = open(telFile[:-4] + '_to_fix.txt','w')
    ofile.write('Missing Parts:\n')
    ofile.write('\n'.join(missing))
    ofile.write('\n\nParts with Invalid Pins:\n')
    ofile.write('\n'.join(invalid))
    ofile.close()