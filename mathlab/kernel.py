"""Six bounded mathematical models, independent of renderers and browser state.

All geometry is a sampled view, never the authority for a theorem. Analytic
references and numeric-method diagnostics retain their own names and scopes.
"""
from math import ceil, cos, exp, isfinite, pi, sin, sqrt

from .catalog import catalog, lesson_spec

CYAN = [.28, .84, 1.0]
AMBER = [1.0, .73, .32]
PINK = [1.0, .35, .66]
MINT = [.36, 1.0, .73]
VIOLET = [.65, .55, 1.0]
QUIET = [.12, .25, .39]
WHITE = [.83, .91, 1.0]


def normalize_params(lesson_id, params=None):
    spec = lesson_spec(lesson_id)
    if params is None:
        params = {}
    if not isinstance(params, dict):
        raise ValueError("Parameters must be a JSON object.")
    names = {p["id"] for p in spec["parameters"]}
    unknown = set(params) - names
    if unknown:
        raise ValueError("Unknown parameter(s): " + ", ".join(sorted(map(str, unknown))))
    result = {}
    for p in spec["parameters"]:
        value = params.get(p["id"], p["default"])
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(p["id"] + " must be a finite number.")
        if not p["min"] <= value <= p["max"] or not isfinite(value):
            raise ValueError(f"{p['id']} must be between {p['min']} and {p['max']}.")
        if p["type"] == "integer":
            if int(value) != value:
                raise ValueError(p["id"] + " must be an integer.")
            value = int(value)
        result[p["id"]] = value
    return result


def _line(primitives, name, points, color=CYAN):
    primitives.append({"kind": "line", "id": name, "points": [list(p) for p in points], "color": color[:]})


def _sphere(primitives, name, point, radius=.07, color=AMBER):
    primitives.append({"kind": "sphere", "id": name, "position": list(point), "radius": radius, "color": color[:]})


def _metric(name, label, value, unit="", note=""):
    return {"id": name, "label": label, "value": value, "unit": unit, "note": note}


def _axes(primitives, xmin, xmax, ymin, ymax, z=0):
    _line(primitives, "axis_x", [[xmin, 0, z], [xmax, 0, z]], [.27, .43, .58])
    _line(primitives, "axis_y", [[0, ymin, z], [0, ymax, z]], [.27, .43, .58])


def _geometry_bounds(primitives):
    """Enclose the sampled display, including marker radii, not a typical orbit."""
    lower=[float("inf")]*3
    upper=[float("-inf")]*3
    for primitive in primitives:
        points=primitive.get("points",[])
        if primitive["kind"]=="sphere":
            center=primitive["position"];radius=primitive["radius"]
            points=[[v-radius for v in center],[v+radius for v in center]]
        elif primitive["kind"]=="box":
            center=primitive["position"];size=primitive["size"]
            points=[[v-s/2 for v,s in zip(center,size)],
                    [v+s/2 for v,s in zip(center,size)]]
        for point in points:
            for axis,value in enumerate(point):
                lower[axis]=min(lower[axis],value)
                upper[axis]=max(upper[axis],value)
    padding=[max(.25,(hi-lo)*.05) for lo,hi in zip(lower,upper)]
    return {"center":[(lo+hi)/2 for lo,hi in zip(lower,upper)],
            "size":[hi-lo+2*pad for lo,hi,pad in zip(lower,upper,padding)]}


def _linear(p):
    a, b, c, d, t = (p[k] for k in ("a", "b", "c", "d", "blend"))
    A, B, C, D = 1+t*(a-1), t*b, t*c, 1+t*(d-1)
    transform = lambda x, y: [A*x+B*y, C*x+D*y, .04]
    primitives = []
    for i in range(-4, 5):
        _line(primitives, f"original_v{i}", [[i,-4,-.04],[i,4,-.04]], QUIET)
        _line(primitives, f"original_h{i}", [[-4,i,-.04],[4,i,-.04]], QUIET)
        _line(primitives, f"moved_v{i}", [transform(i,-4),transform(i,4)], CYAN)
        _line(primitives, f"moved_h{i}", [transform(-4,i),transform(4,i)], CYAN)
    _line(primitives, "unit_circle", [[cos(i*2*pi/128),sin(i*2*pi/128),0] for i in range(129)], QUIET)
    _line(primitives, "ellipse", [transform(cos(i*2*pi/128),sin(i*2*pi/128)) for i in range(129)], AMBER)
    _line(primitives, "basis_x", [[0,0,.1], transform(1,0)], PINK)
    _line(primitives, "basis_y", [[0,0,.1], transform(0,1)], MINT)
    _sphere(primitives,"basis_x_tip",transform(1,0),.10,PINK)
    _sphere(primitives,"basis_y_tip",transform(0,1),.10,MINT)
    primitives.append({"kind":"mesh","id":"unit_square_image","points":[transform(0,0),transform(1,0),transform(1,1),transform(0,1)],"indices":[0,1,2,3,-1],"color":MINT[:],"transparency":.7})
    det = A*D-B*C
    disc = (A-D)**2+4*B*C
    real = disc >= 0
    residuals, eigenvalues = [], []
    if real:
        for i, lam in enumerate(((A+D+sqrt(max(0,disc)))/2,(A+D-sqrt(max(0,disc)))/2)):
            # Pick the longer row-perpendicular candidate; scalar matrices permit any direction.
            x,y = (B,lam-A) if B*B+(lam-A)**2 >= (lam-D)**2+C*C else (lam-D,C)
            length=sqrt(x*x+y*y)
            if length<1e-12:
                x,y=(1.,0.) if i==0 else (0.,1.)
            else:
                x,y=x/length,y/length
            residuals.append(sqrt((A*x+B*y-lam*x)**2+(C*x+D*y-lam*y)**2))
            eigenvalues.append(lam)
            _line(primitives,f"eigenline_{i}",[[-4*x,-4*y,.12],[4*x,4*y,.12]], VIOLET)
    extent = max(5., 4*(abs(A)+abs(B)), 4*(abs(C)+abs(D)))
    return primitives, [
        _metric("determinant","Signed area factor",det,"×","Determinant of the displayed B(t), not only the target A."),
        _metric("area_scale","Area magnitude",abs(det),"×"),
        _metric("eigenvalues","Real eigenvalues",", ".join(f"{v:.5g}" for v in eigenvalues) if real else "complex pair","","No real eigenlines are drawn for a complex pair."),
        _metric("eigen_residual","Eigenvector residual",max(residuals) if real else "not applicable","","||Bv−λv|| for normalized drawn eigenvectors; floating-point diagnostic.")
    ], {"center":[0,0,0],"size":[2*extent,2*extent,0]}, {
        "matrix":[[A,B],[C,D]],"target_matrix":[[a,b],[c,d]],"determinant":det,"real_eigenvalues":eigenvalues,
        "eigen_discriminant":disc}, ["Cyan geometry is the displayed interpolated matrix B(t).", "A line can retain its direction while reversing its arrow when its eigenvalue is negative."]


def _derivative(p):
    x,h=p["x"],p["h"]
    f=lambda q:sin(q)+.15*q*q
    exact=cos(x)+.3*x
    forward=(f(x+h)-f(x))/h
    central=(f(x+h)-f(x-h))/(2*h)
    primitives=[]
    _axes(primitives,-4.2,4.2,-1.8,3.5)
    _line(primitives,"curve",[[q/40,f(q/40),0] for q in range(-168,169)],CYAN)
    _line(primitives,"tangent",[[x-1.4,f(x)-1.4*exact,.08],[x+1.4,f(x)+1.4*exact,.08]],PINK)
    _line(primitives,"secant",[[x-h*.25,f(x)-h*.25*forward,.12],[x+h*1.25,f(x)+h*1.25*forward,.12]],AMBER)
    _line(primitives,"rise_run",[[x,f(x),.14],[x+h,f(x),.14],[x+h,f(x+h),.14]],MINT)
    _line(primitives,"central_secant",[[x-h,f(x-h),.03],[x+h,f(x+h),.03]],VIOLET)
    _sphere(primitives,"at_x",[x,f(x),.16],.09,PINK)
    _sphere(primitives,"at_x_plus_h",[x+h,f(x+h),.16],.08,AMBER)
    return primitives,[
        _metric("analytic","Analytic tangent slope",exact),_metric("forward","Forward secant slope",forward),
        _metric("forward_error","Forward absolute error",abs(forward-exact)),
        _metric("central_error","Central absolute error",abs(central-exact)),
        _metric("central_bound","Central error bound",h*h/6,"","Analytic bound from |f‴|≤1; the quadratic contributes zero central-difference truncation error.")
    ],{"center":[0,.9,0],"size":[9,6,0]}, {"f_x":f(x),"f_x_h":f(x+h),"analytic_slope":exact,"forward_slope":forward,"central_slope":central,"central_bound":h*h/6}, ["Pink is the analytic tangent; amber is the forward secant; violet is the symmetric secant.","This experiment samples a known smooth function; it does not infer a derivative of arbitrary data."]


def _integral(p):
    a,b,n,sample=(p[k] for k in ("a","b","n","sample"))
    f=lambda q:.25*q*q+.35*cos(2*q)+1.2
    F=lambda q:q**3/12+.175*sin(2*q)+1.2*q
    dx=(b-a)/n
    heights=[f(a+(i+(sample+1)/2)*dx) for i in range(n)]
    approx=sum(heights)*dx;exact=F(b)-F(a)
    primitives=[]
    _axes(primitives,-3.3,3.3,0,4)
    _line(primitives,"integrand",[[q/50,f(q/50),.11] for q in range(-160,161)],AMBER)
    for i,height in enumerate(heights):
        primitives.append({"kind":"box","id":f"rectangle_{i}","position":[a+(i+.5)*dx,height/2,-.03],"size":[dx,height,.18],"color":MINT[:],"transparency":.30})
        _sphere(primitives,f"sample_{i}",[a+(i+(sample+1)/2)*dx,height,.16],min(.045,dx*.12),PINK)
    bound=1.9*(b-a)**3/(24*n*n)
    return primitives,[
        _metric("approximation","Rectangle sum",approx,"area units"),_metric("reference","Analytic integral",exact,"area units"),
        _metric("signed_error","Approximation − reference",approx-exact,"area units"),
        _metric("width","Rectangle width",dx),
        _metric("midpoint_bound","Midpoint absolute-error bound",bound if sample==0 else "not applicable","","The midpoint rule only; |f″|≤1.9.")
    ],{"center":[0,1.8,0],"size":[7,4.4,.6]}, {"approximation":approx,"reference":exact,"signed_error":approx-exact,"dx":dx,"heights":heights,"midpoint_bound":bound,"rule":{-1:"left",0:"midpoint",1:"right"}[sample]}, ["The pink dot chooses a rectangle's height; its horizontal position depends on the sampling rule.","Positive height makes the displayed integral an ordinary area on this restricted interval."]


def _fourier(p):
    terms,phase=p["terms"],p["phase"]
    partial=lambda t:4/pi*sum(sin((2*k+1)*t)/(2*k+1) for k in range(terms))
    primitives=[];cx,cy=-3.6,0.
    _axes(primitives,.3,7.0,-1.6,1.6)
    for k in range(terms):
        odd=2*k+1;radius=4/(pi*odd)
        _line(primitives,f"epicycle_{k}",[[cx+radius*cos(i*2*pi/64),cy+radius*sin(i*2*pi/64),0] for i in range(65)],VIOLET)
        nx,ny=cx+radius*cos(odd*phase),cy+radius*sin(odd*phase)
        _line(primitives,f"phasor_{k}",[[cx,cy,.05],[nx,ny,.05]],MINT)
        cx,cy=nx,ny
    _sphere(primitives,"epicycle_tip",[cx,cy,.12],.085,AMBER)
    wave_x=lambda t:.45+t
    _line(primitives,"partial_wave",[[wave_x(t*2*pi/512),partial(t*2*pi/512),.03] for t in range(513)],CYAN)
    _line(primitives,"positive_plateau",[[wave_x(0),1,-.04],[wave_x(pi),1,-.04]],QUIET)
    _line(primitives,"negative_plateau",[[wave_x(pi),-1,-.04],[wave_x(2*pi),-1,-.04]],QUIET)
    _sphere(primitives,"wave_tip",[wave_x(phase),cy,.12],.085,AMBER)
    _line(primitives,"shared_phase",[[cx,cy,.06],[wave_x(phase),cy,.06]],AMBER)
    mse=max(0,1-8/(pi*pi)*sum(1/(2*k+1)**2 for k in range(terms)))
    peak=max(partial(i*pi/2048) for i in range(2049))
    return primitives,[
        _metric("value","Current partial sum",partial(phase)),_metric("harmonic","Highest harmonic",2*terms-1),
        _metric("rms_error","Exact whole-period RMS error",sqrt(mse),"","Parseval tail relative to the ±1 square wave; not maximum pointwise error."),
        _metric("overshoot","Sampled excess above +1",max(0,peak-1)*100,"% of plateau","Maximum over 2,049 phase samples in [0,π]; not an analytic maximum.")
    ],{"center":[.7,0,0],"size":[13.5,5,0]}, {"partial_value":partial(phase),"tip":[cx,cy],"rms_error":sqrt(mse),"sampled_peak":peak}, ["The epicycle endpoint's height and wave dot use the same arithmetic sum.","RMS convergence and visible ringing describe different error measures. No vertical segment is drawn as if it were a value of the discontinuous target."]


def _lorenz_rhs(state,sigma,rho,beta):
    x,y,z=state
    return (sigma*(y-x),x*(rho-z)-y,x*y-beta*z)


def _rk4_lorenz(state,h,sigma,rho,beta):
    k1=_lorenz_rhs(state,sigma,rho,beta)
    k2=_lorenz_rhs(tuple(q+h*v/2 for q,v in zip(state,k1)),sigma,rho,beta)
    k3=_lorenz_rhs(tuple(q+h*v/2 for q,v in zip(state,k2)),sigma,rho,beta)
    k4=_lorenz_rhs(tuple(q+h*v for q,v in zip(state,k3)),sigma,rho,beta)
    return tuple(q+h*(u+2*v+2*w+r)/6 for q,u,v,w,r in zip(state,k1,k2,k3,k4))


def _lorenz(p):
    sigma,rho,beta,dt,duration,separation=(p[k] for k in ("sigma","rho","beta","dt","duration","separation"))
    n=ceil(duration/dt);h=duration/n
    state=(1.,1.,1.);other=(1.+separation,1.,1.);fine=state
    first=[state];second=[other];stride=max(1,ceil(n/1400))
    for i in range(n):
        state=_rk4_lorenz(state,h,sigma,rho,beta)
        other=_rk4_lorenz(other,h,sigma,rho,beta)
        fine=_rk4_lorenz(_rk4_lorenz(fine,h/2,sigma,rho,beta),h/2,sigma,rho,beta)
        if i%stride==stride-1 or i==n-1:first.append(state);second.append(other)
    if not all(isfinite(v) for xyz in first+second for v in xyz):raise ValueError("Integration became nonfinite.")
    display=lambda xyz:[xyz[0]*.36,(xyz[2]-23)*.36,xyz[1]*.36]
    primitives=[]
    _line(primitives,"base_trajectory",[display(v) for v in first],CYAN)
    _line(primitives,"nearby_trajectory",[display(v) for v in second],PINK)
    _sphere(primitives,"base_endpoint",display(state),.16,CYAN)
    _sphere(primitives,"nearby_endpoint",display(other),.16,PINK)
    _sphere(primitives,"equilibrium_origin",display((0,0,0)),.12,AMBER)
    if rho>1:
        e=sqrt(beta*(rho-1))
        for sign in (-1,1):_sphere(primitives,f"equilibrium_{sign}",display((sign*e,sign*e,rho-1)),.13,AMBER)
    separation_final=sqrt(sum((a-b)**2 for a,b in zip(state,other)))
    refinement=sqrt(sum((a-b)**2 for a,b in zip(state,fine)))
    return primitives,[
        _metric("separation","Nearby-start endpoint separation",separation_final,"state units","Same RK4 step; different initial x."),
        _metric("refinement","Same-start endpoint difference h vs h/2",refinement,"state units","A refinement diagnostic, not a rigorous global error bound."),
        _metric("actual_step","Actual RK4 step",h,"s","Adjusted downward to end at the requested duration exactly."),
        _metric("steps","Base integration steps",n),
        _metric("divergence","Analytic flow divergence",-(sigma+1+beta),"1/s","Negative volume divergence alone does not establish chaos.")
    ],_geometry_bounds(primitives), {"initial":[1,1,1],"nearby_initial":[1+separation,1,1],"endpoint":list(state),"nearby_endpoint":list(other),"fine_endpoint":list(fine),"h":h,"steps":n,"separation":separation_final,"refinement":refinement}, ["Displayed coordinates map physical (x,y,z) to (0.36x,0.36(z−23),0.36y) so height shows the Lorenz z coordinate. The camera bounds enclose the actual sampled trajectories and markers.","Finite-time sensitivity depends on parameters and duration. The scene does not estimate a Lyapunov exponent or prove an attractor."]


def _gradient(p):
    rate,k,x,y,steps=(p[q] for q in ("rate","condition","start_x","start_y","steps"))
    co,si=cos(.4),sin(.4)
    modes=lambda a,b:(co*a+si*b,-si*a+co*b)
    loss=lambda a,b:.5*(modes(a,b)[0]**2+k*modes(a,b)[1]**2)
    height=.6/sqrt(k)
    display=lambda a,b:[a,loss(a,b)*height,b]
    initial=(x,y);path=[[x,y]]
    losses=[loss(x,y)]
    for _ in range(steps):
        u,v=modes(x,y)
        gx,gy=co*u-si*k*v,si*u+co*k*v
        x,y=x-rate*gx,y-rate*gy
        path.append([x,y]);losses.append(loss(x,y))
    u0,v0=modes(*initial)
    un,vn=u0*(1-rate)**steps,v0*(1-rate*k)**steps
    reference=[co*un-si*vn,si*un+co*vn]
    relative=sqrt((x-reference[0])**2+(y-reference[1])**2)/(1+sqrt(x*x+y*y))
    points=[];indices=[];side=31
    for j in range(side):
        for i in range(side):points.append(display(-3+6*i/(side-1),-3+6*j/(side-1)))
    for j in range(side-1):
        for i in range(side-1):
            v=j*side+i;indices.extend([v,v+1,v+1+side,v+side,-1])
    primitives=[{"kind":"mesh","id":"quadratic_surface","points":points,"indices":indices,"color":VIOLET[:],"transparency":.66}]
    for c in range(-3,4):
        _line(primitives,f"surface_u{c}",[display(c,-3+6*j/60) for j in range(61)],QUIET)
        _line(primitives,f"surface_v{c}",[display(-3+6*j/60,c) for j in range(61)],QUIET)
    shown=[]
    for i,(a,b) in enumerate(path):
        if abs(a)>3.4 or abs(b)>3.4:break
        pos=display(a,b);pos[1]+=.045;shown.append(pos)
        _sphere(primitives,f"iterate_{i}",pos,.065 if i else .11,AMBER if i else MINT)
    if len(shown)>1:_line(primitives,"descent_path",shown,AMBER)
    _sphere(primitives,"minimum",[0,.08,0],.11,PINK)
    q=max(abs(1-rate),abs(1-rate*k))
    regime="contracts every mode" if q<1-1e-12 else "neutral mode boundary" if abs(q-1)<=1e-12 else "some modes amplify"
    maxheight=max(v[1] for v in points+shown)
    return primitives,[
        _metric("loss","Final numeric loss",losses[-1],"","The complete requested iteration, including values outside the displayed domain."),
        _metric("contraction","Worst-case mode factor",q,"× per step",regime),
        _metric("limit","Strict stability limit α <",2/k),
        _metric("recurrence_residual","Relative endpoint/reference difference",relative,"","Independent eigen-coordinate closed form checks the iteration."),
        _metric("shown","Displayed iterates",len(shown),f"of {steps+1}","The path stops drawing before leaving |x|,|y|≤3.4; numeric data retains every iterate.")
    ],{"center":[0,maxheight/2,0],"size":[8,max(2,maxheight+1),8]}, {"iterates":path,"losses":losses,"reference_endpoint":reference,"relative_residual":relative,"contraction_factor":q,"stability_limit":2/k,"shown_iterates":len(shown),"display_truncated":len(shown)<len(path),"rotation_radians":.4}, ["Surface height is scaled by 0.6/√κ for viewing; metric losses remain in the original mathematical units.","A factor above one means some modes amplify. A special start exactly on another eigendirection need not diverge."]


_MODELS={"linear":_linear,"derivative":_derivative,"integral":_integral,"fourier":_fourier,"lorenz":_lorenz,"gradient":_gradient}


def evaluate(lesson_id, params=None):
    """Validate a bounded lesson configuration and return sampled geometry/data."""
    p=normalize_params(lesson_id,params)
    primitives,metrics,_authored_bounds,numerics,insights=_MODELS[lesson_id](p)
    # Every allowed configuration owns its geometry envelope. Typical/default
    # extents cannot safely frame a changed matrix, epicycle or trajectory.
    bounds=_geometry_bounds(primitives)
    spec=lesson_spec(lesson_id)
    return {"schema":"mathlab.sample/1","lesson":lesson_id,"title":spec["title"],"params":p,
            "primitives":primitives,"metrics":metrics,"bounds":bounds,"numerics":numerics,
            "insights":insights,"formula":spec["formula"],
            "scope":"Bounded sampled mathematical model; source equations and diagnostic meanings are declared per lesson. Geometry is not a proof or a complete interactive savegame."}
