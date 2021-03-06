# 2014.10.20 12:27:28 CEST
import jpype
import glob
import os
jars = ('/home/ridderl/cdk/cdk-1.4.13.jar',)
classpath = ':'.join([ os.path.abspath(jar) for jar in jars ])
os.environ['JAVA_HOME'] = '/usr/lib/jvm/java-1.7.0-openjdk-amd64'
jpype.startJVM(jpype.getDefaultJVMPath(), '-ea', '-Djava.class.path=' + classpath)

class engine(object):

    def __init__(self):
        self.cdk = jpype.JPackage('org').openscience.cdk
        self.java = jpype.java
        self.builder = self.cdk.DefaultChemObjectBuilder.getInstance()
        self.sp = self.cdk.smiles.SmilesParser(self.builder)
        self.sp.setPreservingAromaticity(True)
        self.sg = self.cdk.smiles.SmilesGenerator()
        self.sg.setUseAromaticityFlag(True)
        self.isof = self.cdk.config.IsotopeFactory.getInstance(self.builder)
        self.Hmass = self.isof.getMajorIsotope('H').getExactMass().floatValue()
        self.acm = self.cdk.tools.manipulator.AtomContainerManipulator



    def MolToMolBlock(self, molecule):
        mol2stringio = self.java.io.StringWriter()
        mol2writer = self.cdk.io.MDLV2000Writer(mol2stringio)
        try:
            dbst = self.cdk.smiles.DeduceBondSystemTool()
            molecule = dbst.fixAromaticBondOrders(molecule)
        except:
            pass
        mol2writer.write(molecule)
        return mol2stringio.toString()



    def MolFromMolBlock(self, mol_block):
        stringio2mol = self.java.io.StringReader(mol_block)
        reader2mol = self.cdk.io.MDLReader(stringio2mol)
        molecule = self.cdk.Molecule()
        reader2mol.read(molecule)
        self.cdk.tools.manipulator.AtomContainerManipulator.percieveAtomTypesAndConfigureAtoms(molecule)
        self.cdk.aromaticity.CDKHueckelAromaticityDetector.detectAromaticity(molecule)
        ha = self.cdk.tools.CDKHydrogenAdder.getInstance(self.builder)
        ha.addImplicitHydrogens(molecule)
        return molecule



    def generateCoordinates(self, molecule):
        sdg = self.cdk.layout.StructureDiagramGenerator(molecule)
        sdg.generateCoordinates()
        return sdg.getMolecule()



    def MolFromSmiles(self, smiles):
        molecule = self.sp.parseSmiles(smiles)
        self.cdk.tools.manipulator.AtomContainerManipulator.percieveAtomTypesAndConfigureAtoms(molecule)
        self.cdk.aromaticity.CDKHueckelAromaticityDetector.detectAromaticity(molecule)
        ha = self.cdk.tools.CDKHydrogenAdder.getInstance(self.builder)
        ha.addImplicitHydrogens(molecule)
        molecule = self.generateCoordinates(molecule)
        return molecule



    def MolToSmiles(self, molecule):
        return self.sg.createSMILES(molecule)



    def MolToInchiKey(self, molecule):
        mol = molecule.clone()
        for x in range(mol.getBondCount()):
            mol.getBond(x).setFlag(5, 0)

        igf = self.cdk.inchi.InChIGeneratorFactory.getInstance()
        ig = igf.getInChIGenerator(mol)
        return ig.getInchiKey()



    def GetFormulaProps(self, mol):
        formula = self.cdk.tools.manipulator.MolecularFormulaManipulator.getMolecularFormula(mol)
        formula_string = self.cdk.tools.manipulator.MolecularFormulaManipulator.getString(formula)
        mim = self.cdk.tools.manipulator.MolecularFormulaManipulator.getMajorIsotopeMass(formula)
        return (mim, formula_string)



    def FragmentToSmiles(self, mol, atomlist):
        return self.sg.createSMILES(self.acm.extractSubstructure(mol, atomlist))



    def FragmentToInchiKey(self, mol, atomlist):
        ac = self.acm.extractSubstructure(mol, atomlist)
        return self.MolToInchiKey(ac)



    def LogP(self, mol):
        ha = self.cdk.tools.CDKHydrogenAdder.getInstance(self.builder)
        newmol = mol.clone()
        ha.addImplicitHydrogens(newmol)
        self.acm.convertImplicitToExplicitHydrogens(newmol)
        xlpd = self.cdk.qsar.descriptors.molecular.XLogPDescriptor()
        return xlpd.calculate(newmol).getValue().toString()



    def natoms(self, mol):
        return mol.getAtomCount()



    def GetExtendedAtomMass(self, mol, atom):
        mass = self.isof.getMajorIsotope(mol.getAtom(atom).getSymbol()).getExactMass().floatValue()
        try:
            hc = mol.getAtom(atom).getImplicitHydrogenCount().intValue()
        except:
            hc = 0
        return mass + self.Hmass * hc



    def GetAtomSymbol(self, mol, atom):
        return mol.getAtom(atom).getSymbol()



    def GetAtomHs(self, mol, atom):
        return mol.getAtom(atom).getImplicitHydrogenCount().intValue()



    def nbonds(self, mol):
        return mol.getBondCount()



    def GetBondAtoms(self, mol, bond):
        atoms = []
        for a in mol.getBond(bond).atoms().iterator():
            atoms.append(mol.getAtomNumber(a))

        return atoms



    def GetNBonds(self, mol, atom):
        neighbours = mol.getAtom(atom).getFormalNeighbourCount().intValue()
        hydrogens = mol.getAtom(atom).getImplicitHydrogenCount().intValue()
        return neighbours - hydrogens



    def GetBondType(self, mol, bond):
        if mol.getBond(bond).getFlag(4) == 1:
            return 'AROMATIC'
        else:
            return mol.getBond(bond).getOrder().toString()
