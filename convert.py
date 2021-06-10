import svgwrite
import svgelements

svg = svgelements.SVG.parse('<Filename Here>')
elements = []
for element in svg.elements():
	try:
		if element.values['visibility'] == 'hidden':
			continue
	except (KeyError, AttributeError):
		pass
	# An example of some processing, only keep large shapes
	if isinstance(element, svgelements.Shape):
		ebbox = element.bbox()
		h = ebbox[3] - ebbox[1]
		w = ebbox[2] - ebbox[0]
		eArea = h*w
		if eArea > 10.0:
			elements.append(element)
	else:
		pass


# To get the extra parameters for the svgwrite objects
# we build a keyword argument dictionary.

#Parameters:
#    eleAttrs (dict):   The element's "values" dictionary, contains all information
#			about the tag in a parsable format
#
#    noList   (list):   A list of information in the "values" dictionary which is
#			either already used, or doesn't contribute to the look
#			of the element

#Returns:
#    extrakw  (dict):   A dictionary representing (keyword, value) pairs for the
#			svgwrite initalization functions

def buildExtra(eleAttrs, noList, custAttrs={}):
	noList.extend(['tag','attributes',''])
	extrakw = {}
	for kw, kv in eleAttrs.items():
		if kw in noList:
			continue
		if kv == "":
			continue
		kw = kw.strip().replace("-","_")
		kv = kv.strip()
		#Special Cases
		if kw == "stroke_dasharray":
			kv = [int(x.strip()) for x in kv.split(",")]
		
		if kw in custAttrs.keys():
			extrakw[kw] = custAttrs[kw]
		else:
			extrakw[kw] = kv
	return extrakw

# The new svg image which our elements will be written to
D = svgwrite.drawing.Drawing(filename="cleaned_fig.svg", size=(svg.width, svg.height))
typeExamp = {}
for element in elements:
	# using element.values allows us to iterate through all
	# the extraneous parameters associated with the element
	# while also accessing it's type easily
	eleType = element.values['tag']
	eleAttrs = element.values
	curEle = None
	if eleType == 'line':
		extrakw = buildExtra(eleAttrs, ['x1','y1','x2','y2','width','height'])
		lineS = (element.x1, element.y1)
		lineE = (element.x2, element.y2)
		curEle = svgwrite.shapes.Line(lineS,lineE,**extrakw)
	elif eleType == 'path':
		extrakw = buildExtra(eleAttrs, ['width','height','pathd_loaded','d'])
		reEl = element.reify()
		pathD = reEl.d()
		curEle = svgwrite.path.Path(d=pathD, **extrakw)
	elif eleType == 'rect':
		extrakw = buildExtra(eleAttrs, ['x','y','width','height'])
		reIn = (element.x, element.y)
		reSi = (element.width, element.height)
		curEle = svgwrite.shapes.Rect(insert=reIn, size=reSi, **extrakw)
	elif eleType == 'polygon':
		extrakw = buildExtra(eleAttrs, ['points','width','height'])
		polPo = element.points
		curEle = svgwrite.shapes.Polygon(points=polPo, **extrakw)
	else:
		#If it is an unsupported object, print out some information at
		#the end which will allow us to write a parser for it
		typeExamp[curEle] = eleAttrs


	if curEle is not None:
		if element.id is not None:
			curEle.update({"id":element.id})
		D.add(curEle)

#Save the svg
D.save(pretty=True)

#Print out the unsupported objects
if len(typeExamp) > 0:
	print("Unable to parse every object found")
	for kk, vv in typeExamp.items():
		print("Type : ", kk)
		print("----------------------")
		print(vv)
		print("")
		print("======================")
		print("")
