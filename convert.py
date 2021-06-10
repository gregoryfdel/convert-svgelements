import svgwrite
import svgelements as svgelements

svg = svgelements.SVG.parse('run_97279_54.svg')
elements = []
for element in svg.elements():
	try:
		if element.values['visibility'] == 'hidden':
			continue
	except (KeyError, AttributeError):
		pass
	if isinstance(element, svgelements.Shape):
		ebbox = element.bbox()
		h = ebbox[3] - ebbox[1]
		w = ebbox[2] - ebbox[0]
		eArea = h*w
		if eArea > 10.0:
			elements.append(element)
	else:
		pass



def buildExtra(eleAttrs, noList):
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
		extrakw[kw] = kv
	return extrakw

D = svgwrite.drawing.Drawing(filename="cleaned_fig.svg", size=(svg.width, svg.height))
typeExamp = {}
for element in elements:
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
		typeExamp[curEle] = eleAttrs


	if curEle is not None:
		D.add(curEle)

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
