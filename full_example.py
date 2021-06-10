import svgwrite
import svgelements
import numpy as np

def addToDict(ddi,topLK,subLK):
	if topLK in ddi.keys():
		ddi[topLK].append(subLK)
	else:
		ddi[topLK] = [subLK]

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


def addElements(svgwriteObj, elementList, **extraprops):
	typeExamp = {}
	drawnElements = []
	for element in elementList:
		eleType = element.values['tag']
		eleAttrs = element.values
		curEle = None
		if eleType == 'line':
			extrakw = buildExtra(eleAttrs, ['x1','y1','x2','y2','width','height'], extraprops)
			lineS = (element.x1, element.y1)
			lineE = (element.x2, element.y2)
			curEle = svgwrite.shapes.Line(lineS,lineE,**extrakw)
		elif eleType == 'path':
			extrakw = buildExtra(eleAttrs, ['width','height','pathd_loaded','d'], extraprops)
			reEl = element.reify()
			pathD = reEl.d()
			curEle = svgwrite.path.Path(d=pathD, **extrakw)
		elif eleType == 'rect':
			extrakw = buildExtra(eleAttrs, ['x','y','width','height'], extraprops)
			reIn = (element.x, element.y)
			reSi = (element.width, element.height)
			curEle = svgwrite.shapes.Rect(insert=reIn, size=reSi, **extrakw)
		elif eleType == 'polygon':
			extrakw = buildExtra(eleAttrs, ['points','width','height'], extraprops)
			polPo = element.points
			curEle = svgwrite.shapes.Polygon(points=polPo, **extrakw)
		else:
			typeExamp[curEle] = eleAttrs


		if curEle is not None:
			if element.id is not None:
				curEle.update({"id":element.id})
			svgwriteObj.add(curEle)
			drawnElements.append(curEle)
	return typeExamp, drawnElements

def repreCircle(pointL):
	xs = np.array([p[0] for p in pointL])
	ys = np.array([p[1] for p in pointL])
	txc = np.mean(xs)
	tyc = np.mean(ys)
	cirTest = np.var(np.sqrt(np.square(xs-txc) + np.square(ys-tyc)))
	if cirTest < 2.0:
		return True
	return False


def isPathCircle(element):
	elementPts = [[p.x, p.y] for p in element.as_points()]
	return repreCircle(elementPts)



svg = svgelements.SVG.parse('<input filename>.svg')
elementDicts = {}
nEle = 0
for element in svg.elements():
	try:
		if element.values['visibility'] == 'hidden':
			continue
	except (KeyError, AttributeError):
		pass
	# An example of some processing, only keep large shapes
	if isinstance(element, svgelements.Shape):
		if element.values['tag'] == "path":
			element = element.reify()
			if len(element) < 5:
				continue
		eleVals = element.values
		ebbox = element.bbox()
		h = ebbox[3] - ebbox[1]
		w = ebbox[2] - ebbox[0]
		eArea = h*w
		eleType = eleVals['tag']
		if (eleType == "path") and (eArea > 10.0) and (eleVals['fill'] == 'none') and (eleVals['stroke'] == r"#999999"):
			element.id = "small"
			addToDict(elementDicts, eleType, element)
		elif (eleType == "path") and (eArea > 10.0) and (not isPathCircle(element)):
			element.id = "large"
			addToDict(elementDicts, eleType, element)
		elif (eleType == "rect") and (eArea > 10.0):
			if (abs(element.width - svg.width) > 5) or (abs(element.height - svg.height) > 5):
				addToDict(elementDicts, eleType, element)
		else:
			pass
	else:
		pass

D = svgwrite.drawing.Drawing(filename="cleaned_fig.svg", size=(svg.width, svg.height))
typeExamp, drawnEle = addElements(D, elementDicts['rect'], stroke='#000000', stroke_width=3, stroke_opacity=1.0)
typeExamp, drawnEle  = addElements(D, elementDicts['path'])

curS = svgwrite.container.Style('''
#small {
	stroke:#BBBBBB;
}

#large {
	stroke:#403f47;
	stroke-dasharray:4;
}

''')

D.defs.add(curS)

D.save(pretty=True)

if len(typeExamp) > 0:
	print("Unable to parse every object found")
	for kk, vv in typeExamp.items():
		print("Type : ", kk)
		print("----------------------")
		print(vv)
		print("")
		print("======================")
		print("")
