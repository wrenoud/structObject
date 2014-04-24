import sys
import unittest
import struct

sys.path += ['..']
from structObject import *
from structField import *

class Point(structObject):
    "Basic point class"
    _field_order = ('x','y')
    x = ctype_double()
    y = ctype_double()

class Point3D(structObject):
    "Basic point class"
    _field_order = ('x','y','z')
    x = ctype_double()
    y = ctype_double()
    z = ctype_double()
    
class BoundingBox(structObject):
    _field_order = ('northwest','southeast')
    northwest = Point
    southeast = Point


class structObjectTests(unittest.TestCase):
    # if length is specified it should be an array or 's'
    def testOrder(self):
        # exception should be raised if '_order' not defined in subclass
        # exception should be raise if '_order' defined in subclass that isn't first decendant of structObject
        pass

    def testInitSetByAttribute(self):
        p = Point()
        self.assertEqual(p.items(),[('x', 0.0), ('y', 0.0)])
        p.x = 5000.0
        p.y = 300.5
        self.assertEqual(p.items(),[('x', 5000.0), ('y', 300.5)])

    def testInitImplicitOrder(self):
        p = Point(5000.0, 300.5)
        self.assertEqual(p.items(),[('x', 5000.0), ('y', 300.5)])

    def testInitExplicitNames(self):
        p = Point(y=300.5, x=5000.0)
        self.assertEqual(p.items(),[('x', 5000.0), ('y', 300.5)])

    def testInitMixedOrdering(self):
        p = Point(5000.0, y=300.5)
        self.assertEqual(p.items(),[('x', 5000.0), ('y', 300.5)])

    def testInitImplicitList(self):
        p = Point((5000.0, 300.5))
        self.assertEqual(p.items(),[('x', 5000.0), ('y', 300.5)])

    def testInitExplicitDict(self):
        p = Point({'x':5000.0, 'y':300.5})
        self.assertEqual(p.items(),[('x', 5000.0), ('y', 300.5)])

    def testPack(self):
        p = Point(5000.0, 300.5)
        self.assertEqual(p.pack(), struct.pack('dd', 5000.0, 300.5))

    def testPackWithSubstructure(self):
        bb = BoundingBox(Point(0.0, 10.0), southeast=Point(15.0, 0.0))
        self.assertEqual(bb.pack(), struct.pack('dddd', 0.0, 10.0, 15.0, 0.0))
            
    def testGetItemWithString(self):
        bb = BoundingBox(Point(0.0, 10.0), southeast=Point(15.0, 0.0))
        self.assertEqual(bb['northwest.y'], 10.0)
        self.assertEqual(bb.northwest['y'], 10.0)

    def testGetItemWithInt(self):
        p = Point(5000.0, 300.5)
        self.assertEqual(p[1], 300.5)
        self.assertRaises(IndexError, p.__getitem__, 3)
        
    def testGetItemWithSlice(self):
        p = Point(5000.0, 300.5)
        self.assertEqual(p[:], [5000.0, 300.5])
        self.assertEqual(p[:1], [5000.0])
        self.assertEqual(p[1:], [300.5])

    def testGetItemWithObj(self):
        p = Point(5000.0, 300.5)
        self.assertRaises(Exception, p.__getitem__, int)
        
    def testSetItemWithString(self):
        bb = BoundingBox()
        bb['northwest.y'] = 15.0
        self.assertEqual(bb.northwest.y, 15.0)
        bb.northwest['y'] = 20.0
        self.assertEqual(bb.northwest.y, 20.0)

    def testSetItemWithInt(self):
        p = Point()
        p[1] = 300.5
        self.assertEqual(p.y, 300.5)
        self.assertRaises(IndexError, p.__setitem__, 3, 500.0)

    def testSetItemWithSlice(self):
        p = Point()
        p[:] = [5000.0, 300.5]
        self.assertEqual(p.values(), [5000.0, 300.5])
        p[:1] = [5000.0]
        self.assertEqual(p.x, 5000.0)
        p[1:] = [300.5]
        self.assertEqual(p.y, 300.5)

    def testSetItemWithObj(self):
        p = Point()
        self.assertRaises(Exception, p.__setitem__, int)

    def testOverloading(self):
        class GenericBoundingBox(structObject):
            _field_order = ('northwest','southeast')
            northwest = None
            southeast = None
            
        class BoundingBox3D(GenericBoundingBox):
            northwest = Point3D
            southeast = Point3D
            
        bb = BoundingBox3D(Point3D(10.0,20.0,30.0))
        self.assertEqual(bb.northwest.z, 30.0)

    def testOverloadingNotImplemented(self):
        class GenericBoundingBox(structObject):
            _field_order = ('northwest','southeast')
            northwest = None
            southeast = None
        self.assertRaises(NotImplementedError,GenericBoundingBox)
        
    def testInitWithWrongObjectTypeForField(self):
        self.assertRaises(TypeError, BoundingBox, Point3D())

    def testSetAttrWithWrongObjectTypeForField(self):
        bb = BoundingBox()
        p = Point3D()
        self.assertRaises(TypeError, bb.__setattr__,'northwest', p)

    def testUpdateWithDict(self):
        p = Point()
        p.update({'y':300.5,'x':5000.0})
        self.assertEqual(p.items(),[('x', 5000.0), ('y', 300.5)])

    def testUpdateWithList(self):
        p = Point()
        p.update([('y',300.5),('x',5000.0)])
        self.assertEqual(p.items(),[('x', 5000.0), ('y', 300.5)])

    def testUpdateWithNamed(self):
        p = Point()
        p.update(y=300.5,x=5000.0)
        self.assertEqual(p.items(),[('x', 5000.0), ('y', 300.5)])

    def testUpdateWithBoth(self):
        p = Point()
        p.update({'y':300.5},x=5000.0)
        self.assertEqual(p.items(),[('x', 5000.0), ('y', 300.5)])
        p.update([('y',400.5)],x=6000.0)
        self.assertEqual(p.items(),[('x', 6000.0), ('y', 400.5)])

    def testUpdateWithBothOrderPrecidence(self):
        p = Point()
        p.update({'x':6000.0},x=5000.0)
        self.assertEqual(p.x,5000.0)

    def testUpdateWithBadType(self):
        p = Point()
        self.assertRaises(TypeError, p.update, 5000.0)

    def testUpdateWithTooManyParameters(self):
        p = Point()
        self.assertRaisesRegexp(TypeError, "update expected at most 1 arguments, got 2", p.update, 5000.0, 6000.0)
            
# no exception should be raised if parent has '_order' defined

# trying to define a class with multiple parents should raise exception

# subclass shouldn't redefine order, exception should be raised

# if field attribute is not int or function should raise exception
# edge case, sub sub class has variable segment dependant on field defined in super, is this accesable?

if __name__ == '__main__':
    unittest.main()
    