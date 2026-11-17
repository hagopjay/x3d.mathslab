"""Bounded signal, diffusion and optics models with declared display transforms.

Only standard-library mathematics runs in the local or Pyodide kernels. Shared
geometry helpers are imported when a model evaluates, keeping catalog imports
independent of kernel registration.
"""
from math import asin, cos, exp, floor, fsum, hypot, pi, sin, sqrt


def _p(key, label, lo, hi, step, default, unit="", integer=False):
    return {"id": key, "label": label, "min": lo, "max": hi, "step": step,
            "default": default, "unit": unit,
            "type": "integer" if integer else "number"}


LESSONS = [
    {"id": "aliasing", "title": "Different Motions, Identical Samples",
     "shortName": "The camera can make time lie", "domain": "SAMPLING & SIGNALS",
     "level": "Grade 10–12", "prerequisites": ["Cosine", "Frequency", "Radians"],
     "accent": "#e7a5ff", "view": "planar",
     "tagline": "Matching dots do not determine the motion between them.",
     "formula": "x(t)=cos(2πft+φ)    ·    fₐ=f−k fₛ    ·    x(j/fₛ)=cos(2πfₐj/fₛ+φ)",
     "description": "A fast cyan signal and a violet signed-frequency alias pass through exactly the same amber samples. Change the sampling rate: extra dots can resolve one ambiguity, but finite samples alone never identify an unrestricted continuous signal.",
     "axes": "Horizontal: time 0–2 s (display x=3t−3). Vertical: signal amplitude. Amber dots are samples at j/fₛ; all lines use the same amplitude scale.",
     "parameters": [_p("frequency", "Signal frequency f", .2, 12, .1, 7, "Hz"),
                    _p("sample_rate", "Samples per second fₛ", 1, 16, 1, 8, "Hz", integer=True),
                    _p("phase", "Initial phase φ", -pi, pi, .02, .65, "rad")],
     "story": [{"title": "Trust the dots?", "text": "Compare the cyan and violet curves at each amber dot. Their between-sample motion differs, even though the samples cannot distinguish them."},
               {"title": "Count turns per sample", "text": "Subtract an integer number of complete turns between observations: f and f−kfₛ produce the same phase modulo 2π at every sampling instant. The displayed alias chooses the interval [−fₛ/2,fₛ/2)."},
               {"title": "State the missing assumption", "text": "Sampling above twice a known signal bandwidth permits the classical ideal bandlimited reconstruction theorem. A few matching samples and a smooth drawn curve do not establish that bandwidth assumption or reconstruct an arbitrary signal."}],
     "challenge": {"question": "At f=8 Hz and fₛ=8 Hz, must the samples show a rapidly moving wave?",
                   "answer": "No. Every sample has the same phase modulo 2π, so the samples equal cos φ. A constant signal is indistinguishable at those instants. The fast signal still oscillates between observations."},
     "presets": [{"title": "Seven turns look like minus one", "params": {"frequency": 7, "sample_rate": 8, "phase": .65}, "why": "One extra full turn per sample hides the direction and rate of phase advance."},
                 {"title": "A fast signal looks frozen", "params": {"frequency": 8, "sample_rate": 8, "phase": .65}, "why": "The same phase is observed every time even though the continuous signal moves."},
                 {"title": "More samples, same known band", "params": {"frequency": 7, "sample_rate": 16, "phase": .65}, "why": "Seven hertz lies below this sampling rate's Nyquist frequency; the selected alias equals the original frequency."}],
     "legend": [{"label": "Original continuous signal", "color": "#47d6ff"},
                {"label": "Signed-frequency alias", "color": "#a68cff"},
                {"label": "Indistinguishable samples", "color": "#ffba52"}],
     "resources": [{"title": "Georgia Tech · DSP First: Sampling and Aliasing",
                    "url": "https://dspfirst.gatech.edu/chapters/04samplin/overview.html",
                    "note": "Study spectral replication and the bandlimit assumption behind the sampling theorem; this scene illustrates the ambiguity before reconstruction."}],
     "connections": [{"lesson": "fourier", "why": "A sampled signal can hide frequency components that Fourier analysis separates."},
                     {"lesson": "complex", "why": "Aliasing is phase advance modulo a full rotation."}]},
    {"id": "heat", "title": "Why Fine Detail Melts First",
     "shortName": "Heat erases the small scales", "domain": "DIFFUSION & PARTIAL DIFFERENTIAL EQUATIONS",
     "level": "Undergraduate 2–3", "view": "spatial",
     "prerequisites": ["Exponential decay", "Fourier modes", "Partial derivatives"],
     "accent": "#8affcf", "tagline": "A rough profile smooths without losing its mean.",
     "formula": "uₜ=αuₓₓ    ·    u=1+0.45e^(−αt)cos x+Aₘe^(−αm²t)cos(mx)",
     "description": "A periodic one-dimensional heat equation evolves exactly as two decaying Fourier modes. The transparent sheet shows the full time history; the mint slice shows the chosen time. Fine detail decays m² times faster, while the spatial mean stays one.",
     "axes": "History sheet: horizontal x∈[0,2π] shown as x−π; vertical height=2(u−1); depth=4t/3−2 for time 0–3. Mint selects the current time; cyan is the initial profile.",
     "parameters": [_p("mode", "Fine-scale mode m", 2, 8, 1, 5, integer=True),
                    _p("amplitude", "Initial fine-scale amplitude Aₘ", 0, .45, .01, .4),
                    _p("diffusivity", "Diffusivity α", .05, 1, .01, .25),
                    _p("time", "Evolution time t", 0, 3, .02, .45)],
     "animation": {"parameter": "time", "min": 0, "max": 3, "speed": .28, "mode": "loop"},
     "story": [{"title": "Separate the scales", "text": "At time zero, the broad cosine carries several small ripples. Increase time: the ripple disappears while the broad feature survives. Depth is time, not another physical dimension of the material."},
               {"title": "Read the exponent", "text": "The second x derivative multiplies cos(mx) by −m². Each heat mode therefore decays as exp(−αm²t): halving wavelength makes its decay rate four times larger."},
               {"title": "Name what is conserved", "text": "Periodic boundaries permit no net loss of mean temperature. The spatial mean remains one, while the squared fluctuation about that mean decreases. This is diffusion, unlike the reversible oscillation of the standing-wave lesson."}],
     "challenge": {"question": "If the mean stays fixed, how can the profile lose its peaks and valleys?",
                   "answer": "Heat redistributes between nearby locations. Positive and negative deviations about the mean cancel in the spatial average, but their squares do not: the average stays one while fluctuation energy falls."},
     "presets": [{"title": "Before the smoothing", "params": {"mode": 5, "amplitude": .4, "diffusivity": .25, "time": 0}, "why": "Both modes are visible before diffusion has acted."},
                 {"title": "Ripples gone, broad shape remains", "params": {"mode": 5, "amplitude": .4, "diffusivity": .25, "time": .6}, "why": "The fine mode loses amplitude 25 times faster than the broad mode."},
                 {"title": "Change wavelength, not the law", "params": {"mode": 2, "amplitude": .4, "diffusivity": .25, "time": .6}, "why": "Longer ripples persist longer under exactly the same diffusivity and elapsed time."}],
     "legend": [{"label": "Two-mode history sheet", "color": "#a68cff"},
                {"label": "Initial profile, t=0", "color": "#47d6ff"},
                {"label": "Current time slice", "color": "#5cffba"},
                {"label": "Conserved mean u=1", "color": "#ffba52"}],
     "resources": [{"title": "Jiří Lebl · Notes on Diffy Qs: Heat Equation",
                    "url": "https://www.jirka.org/diffyqs/html/heateq_section.html",
                    "note": "Study separation of variables and Fourier modes for diffusion. Our cosine modes use a periodic domain and also satisfy insulated-end conditions, not fixed-temperature endpoints."}],
     "connections": [{"lesson": "waves", "why": "The same spatial modes oscillate in a wave equation and decay in a heat equation."},
                     {"lesson": "fourier", "why": "Fourier coordinates turn a PDE into independent scalar decay equations."},
                     {"lesson": "integral", "why": "The spatial integral distinguishes conserved mean from decreasing squared fluctuation."}]},
    {"id": "refraction", "title": "The Fastest Route Bends",
     "shortName": "Fermat turns time into a ray", "domain": "OPTICS & VARIATIONAL MATHEMATICS",
     "level": "Undergraduate 1", "view": "planar",
     "prerequisites": ["Pythagoras", "Derivatives", "Angles from a normal"],
     "accent": "#ffc976", "tagline": "A longer geometric path can take less optical time.",
     "formula": "T(q)=n₁√(q²+h₁²)+n₂√((d−q)²+h₂²)    ·    n₁sin θ₁=n₂sin θ₂",
     "description": "Choose where a path crosses a flat interface. Cyan is the straight geometric route, pink is your trial, and mint minimizes optical travel cost between fixed endpoints. The separate lower plot turns Snell's law into the zero slope of a strictly convex cost curve.",
     "axes": "Upper diagram uses physical x,y with interface y=0. Lower inset: horizontal q∈[0,d] mapped to display x∈[−2.5,2.5]; vertical is T(q)−Tmin (no vertical rescaling), shifted below the ray diagram by the baseline recorded in numerical data. Vacuum speed c is normalized to one.",
     "parameters": [_p("n1", "Upper refractive index n₁", 1, 2.5, .05, 1),
                    _p("n2", "Lower refractive index n₂", 1, 2.5, .05, 1.5),
                    _p("height", "Source height h₁", .4, 2, .05, 1.1),
                    _p("depth", "Target depth h₂", .4, 2, .05, 1.2),
                    _p("span", "Horizontal separation d", .5, 4, .05, 3),
                    _p("crossing", "Trial crossing fraction q/d", 0, 1, .01, .5)],
     "story": [{"title": "Optimize a crossing", "text": "Move the pink crossing along the interface. Its optical travel cost is the sum of each segment's length multiplied by the medium's index. The lowest point of the separate cost plot identifies the mint path."},
               {"title": "Differentiate the route", "text": "Changing q lengthens one segment while shortening the other. At the minimum, n₁q/√(q²+h₁²) equals n₂(d−q)/√((d−q)²+h₂²). These ratios are sines of angles measured from the normal, giving Snell's law."},
               {"title": "State the family", "text": "For these fixed endpoints, positive heights and two homogeneous media, the one-crossing travel cost is strictly convex and has one minimum. Fermat's principle is more generally stationary optical path; this scene does not model reflection, interference, or total internal reflection of an independently chosen incident ray."}],
     "challenge": {"question": "If the two refractive indices are equal, must the fastest path bend at the interface?",
                   "answer": "No. Cost becomes a constant times geometric length, so the optimum is the straight line. If indices differ, spending more distance in the faster medium can compensate for a longer total route."},
     "presets": [{"title": "No optical contrast", "params": {"n1": 1.5, "n2": 1.5, "crossing": .5}, "why": "With equal speeds, the minimum coincides with the straight geometric path."},
                 {"title": "Bend toward the normal", "params": {"n1": 1, "n2": 2, "crossing": .5}, "why": "The higher-index medium is slower; its optimum ray makes a smaller angle with the normal."},
                 {"title": "Spend distance upstairs", "params": {"n1": 1, "n2": 2.5, "height": .6, "depth": 1.8, "span": 4, "crossing": .3}, "why": "A large speed contrast makes the time-minimizing route visibly differ from the shortest route."}],
     "legend": [{"label": "Straight geometric route", "color": "#47d6ff"},
                {"label": "Trial crossing and cost", "color": "#ff59a8"},
                {"label": "Minimum-time route and cost", "color": "#5cffba"},
                {"label": "Optical cost above minimum", "color": "#ffba52"}],
     "resources": [{"title": "OpenStax · The Law of Refraction",
                    "url": "https://openstax.org/books/college-physics-2e/pages/25-3-the-law-of-refraction",
                    "note": "Check Snell's law, angle conventions and the relationship between refractive index and propagation speed."},
                   {"title": "The Feynman Lectures · Optics: The Principle of Least Time",
                    "url": "https://www.feynmanlectures.caltech.edu/I_26.html",
                    "note": "Connect the path derivative with refraction and distinguish the stationary-path principle from a blanket shortest-distance rule."}],
     "connections": [{"lesson": "derivative", "why": "The minimum optical travel cost has zero derivative with respect to crossing position."},
                     {"lesson": "lagrange", "why": "A physical path is optimized inside an explicitly constrained family."}]},
]


def _aliasing(p):
    from .kernel import AMBER, CYAN, QUIET, VIOLET, _line, _metric, _sphere

    frequency, sample_rate, phase = (p[key] for key in ("frequency", "sample_rate", "phase"))
    turns_removed = floor(frequency/sample_rate+.5)
    alias = frequency-turns_removed*sample_rate
    signal = lambda t: cos(2*pi*frequency*t+phase)
    alternative = lambda t: cos(2*pi*alias*t+phase)
    times = [2*j/1200 for j in range(1201)]
    sample_times = [j/sample_rate for j in range(2*sample_rate+1)]
    original = [signal(t) for t in times]
    aliased = [alternative(t) for t in times]
    samples = [signal(t) for t in sample_times]
    sample_aliases = [alternative(t) for t in sample_times]
    error = max(abs(a-b) for a,b in zip(samples,sample_aliases))
    primitives = []
    _line(primitives, "time_axis", [[-3,0,-.06],[3,0,-.06]], QUIET)
    for j in range(9):
        x=-3+j*.75
        _line(primitives, f"time_tick_{j}", [[x,-1.2,-.06],[x,1.2,-.06]], QUIET)
    _line(primitives, "original_signal", [[3*t-3,y,0] for t,y in zip(times,original)], CYAN)
    _line(primitives, "alias_signal", [[3*t-3,y,.025] for t,y in zip(times,aliased)], VIOLET)
    for j,(t,value) in enumerate(zip(sample_times,samples)):
        _line(primitives, f"sampling_stem_{j}", [[3*t-3,0,.05],[3*t-3,value,.05]], QUIET)
        _sphere(primitives, f"sample_{j}", [3*t-3,value,.08], .055, AMBER)
    return primitives, [
        _metric("alias", "Signed alias frequency", alias, "Hz", "Representative in [−fₛ/2,fₛ/2); negative means reversed phase advance, not a negative magnitude."),
        _metric("nyquist", "Nyquist frequency fₛ/2", sample_rate/2, "Hz"),
        _metric("samples", "Shared samples in two seconds", len(samples)),
        _metric("sample_error", "Maximum sample disagreement", error, "", "Floating-point diagnostic; the sampled values agree algebraically."),
        _metric("removed", "Whole turns removed per sample", turns_removed),
    ], {}, {"frequency":frequency,"sample_rate":sample_rate,"phase":phase,
            "alias_frequency":alias,"turns_removed":turns_removed,
            "times":times,"original":original,"alias":aliased,
            "sample_times":sample_times,"samples":samples,"alias_samples":sample_aliases,
            "max_sample_error":error,"window_seconds":2,
            "display_time_scale":3,"display_time_offset":-3}, [
        "The curves represent sample-equivalent candidates, not a reconstruction and its error. They can coincide for some controls, including an original frequency below Nyquist; the default reveals distinct between-sample motion. Amber samples alone cannot choose between unrestricted candidates.",
        "At t=j/fₛ their phase difference is an integer multiple of 2π. Frequencies f−kfₛ give an infinite family of sample-equivalent complex phase advances.",
        "The displayed real cosine also has a sign/phase symmetry: a negative signed frequency with phase φ equals a positive frequency with phase −φ. Signed alias is a convenient phase convention.",
        "The classical ideal sampling theorem assumes a known strict bandlimit and an ideal sampling/reconstruction setting. This finite two-second display proves neither arbitrary reconstruction nor frequency uniqueness."]


def _heat(p):
    from .kernel import AMBER, CYAN, MINT, QUIET, VIOLET, _line, _metric

    mode, amplitude, alpha, time = (p[key] for key in ("mode","amplitude","diffusivity","time"))
    broad=.45
    temperature=lambda x,t:1+broad*exp(-alpha*t)*cos(x)+amplitude*exp(-alpha*mode*mode*t)*cos(mode*x)
    energy=lambda t:.5*(broad*broad*exp(-2*alpha*t)+amplitude*amplitude*exp(-2*alpha*mode*mode*t))
    display=lambda x,t:[x-pi,2*(temperature(x,t)-1),4*t/3-2]
    xs=[2*pi*j/256 for j in range(257)]
    current=[temperature(x,time) for x in xs]
    initial=[temperature(x,0) for x in xs]
    # A periodic trapezoid uses the left endpoint once, not both copies of x=0.
    quadrature_mean=fsum(current[:-1])/256
    quadrature_energy=fsum((u-1)**2 for u in current[:-1])/256
    rows,columns=25,49
    points=[display(2*pi*i/(columns-1),3*j/(rows-1)) for j in range(rows) for i in range(columns)]
    indices=[]
    for j in range(rows-1):
        for i in range(columns-1):
            k=j*columns+i;indices.extend([k,k+1,k+columns+1,k+columns,-1])
    primitives=[{"kind":"mesh","id":"diffusion_history","points":points,"indices":indices,
                 "color":VIOLET[:],"transparency":.72}]
    for j in range(13):
        t=3*j/12
        _line(primitives,f"history_slice_{j}",[display(x,t) for x in xs[::4]],QUIET)
    for j in range(9):
        x=2*pi*j/8
        _line(primitives,f"history_position_{j}",[display(x,3*k/48) for k in range(49)],QUIET)
    _line(primitives,"initial_profile",[display(x,0) for x in xs],CYAN)
    _line(primitives,"current_profile",[[x-pi,2*(u-1),4*time/3-2+.025] for x,u in zip(xs,current)],MINT)
    _line(primitives,"current_mean",[[-pi,0,4*time/3-2+.04],[pi,0,4*time/3-2+.04]],AMBER)
    _line(primitives,"mean_time_axis",[[0,0,-2],[0,0,2]],AMBER)
    xprobe=.73;h=.001
    exact_ut=-alpha*broad*exp(-alpha*time)*cos(xprobe)-alpha*mode*mode*amplitude*exp(-alpha*mode*mode*time)*cos(mode*xprobe)
    fd_xx=(temperature(xprobe+h,time)-2*temperature(xprobe,time)+temperature(xprobe-h,time))/(h*h)
    pde_residual=abs(exact_ut-alpha*fd_xx)
    broad_now=broad*exp(-alpha*time)
    fine_now=amplitude*exp(-alpha*mode*mode*time)
    return primitives, [
        _metric("mean","Spatial mean",quadrature_mean,"","Periodic trapezoid; analytic reference is exactly 1."),
        _metric("energy","Mean squared fluctuation",energy(time),"","Spatial average of (u−1)², not total heat or thermodynamic energy."),
        _metric("fine_amplitude","Remaining fine-scale amplitude",fine_now),
        _metric("rate_ratio","Fine / broad decay rate",mode*mode,"×"),
        _metric("pde_residual","Finite-difference PDE residual",pde_residual,"","|analytic uₜ−α·central-difference uₓₓ| at x=.73, h=.001. A stencil diagnostic, not a global error bound."),
    ], {}, {"mode":mode,"amplitude":amplitude,"diffusivity":alpha,"time":time,
            "x":xs,"initial_values":initial,"current_values":current,"mean":1.,
            "quadrature_mean":quadrature_mean,"quadrature_energy":quadrature_energy,
            "fluctuation_energy":energy(time),"initial_fluctuation_energy":energy(0),
            "energy_derivative":-alpha*(broad*broad*exp(-2*alpha*time)+mode*mode*amplitude*amplitude*exp(-2*alpha*mode*mode*time)),
            "broad_amplitude":broad_now,"fine_amplitude":fine_now,
            "fine_to_broad_decay_rate":mode*mode,"broad_decay_rate":alpha,"fine_decay_rate":alpha*mode*mode,
            "pde_probe_x":xprobe,"pde_stencil_h":h,"analytic_ut":exact_ut,"finite_difference_uxx":fd_xx,
            "finite_difference_pde_residual":pde_residual,
            "display_height_scale":2,"history_time_interval":[0,3],"history_depth_scale":4/3,"history_depth_offset":-2}, [
        "The source is an exact two-mode solution of the periodic linear heat equation on length 2π. There is no time-stepping solver, boundary heat loss, or random noise.",
        "The sheet has one spatial coordinate and one time coordinate. Its displayed height is 2(u−1); depth maps time 0…3 to −2…2. This is not a two-dimensional spatial temperature field.",
        "The spatial mean is fixed at one because every nonconstant cosine averages to zero over the periodic domain. Mean squared deviation is ½[0.45²e^(−2αt)+Aₘ²e^(−2αm²t)] and decreases.",
        "Higher spatial frequency creates larger curvature at equal amplitude. The −m² eigenvalue of the second derivative explains faster smoothing without implying that heat travels as a wave.",
        "The finite-difference residual contains spatial truncation and roundoff error. The separately reported periodic integrals check the mean and fluctuation formula against the sampled profile."]


def _refraction(p):
    from .kernel import AMBER, CYAN, MINT, PINK, QUIET, VIOLET, _line, _metric, _sphere

    n1,n2,height,depth,span,crossing=(p[key] for key in ("n1","n2","height","depth","span","crossing"))
    cost=lambda q:n1*hypot(q,height)+n2*hypot(span-q,depth)
    derivative=lambda q:n1*q/hypot(q,height)-n2*(span-q)/hypot(span-q,depth)
    second=lambda q:n1*height*height/(q*q+height*height)**1.5+n2*depth*depth/((span-q)**2+depth*depth)**1.5
    lo,hi=0.,span
    for _ in range(70):
        middle=(lo+hi)/2
        if derivative(middle)<0:lo=middle
        else:hi=middle
    optimum=(lo+hi)/2
    trial=crossing*span
    straight=span*height/(height+depth)
    optimum_cost=cost(optimum);trial_cost=cost(trial);straight_cost=cost(straight)
    source=[0,height,.08];target=[span,-depth,.08]
    centered=lambda point:[point[0]-span/2,point[1],point[2]]
    primitives=[]
    for name,ys,color in (("upper_medium",[0,height+.35],CYAN),("lower_medium",[-depth-.35,0],VIOLET)):
        primitives.append({"kind":"mesh","id":name,
                           "points":[[-.35-span/2,ys[0],-.1],[span/2+.35,ys[0],-.1],
                                     [span/2+.35,ys[1],-.1],[-.35-span/2,ys[1],-.1]],
                           "indices":[0,1,2,3,-1],"color":color[:],"transparency":.94})
    _line(primitives,"interface",[[-span/2-.35,0,0],[span/2+.35,0,0]],QUIET)
    for name,q,color,z in (("straight_path",straight,CYAN,.04),("trial_path",trial,PINK,.08),("minimum_path",optimum,MINT,.12)):
        _line(primitives,name,[centered([0,height,z]),centered([q,0,z]),centered([span,-depth,z])],color)
        _sphere(primitives,name+"_crossing",centered([q,0,z]),.055,color)
    _sphere(primitives,"source",centered(source),.085,AMBER)
    _sphere(primitives,"target",centered(target),.085,AMBER)
    _line(primitives,"normal_at_optimum",[[optimum-span/2,-.5,.02],[optimum-span/2,.5,.02]],QUIET)
    qs=[span*i/240 for i in range(241)]
    costs=[cost(q) for q in qs]
    # Inset and physical rays are intentionally separate diagrams. Their
    # horizontal coordinate maps differ; cost has a declared additive offset.
    plot_baseline=-depth-1-max(costs)+optimum_cost
    plot=lambda q:[-2.5+5*q/span,plot_baseline+cost(q)-optimum_cost,.08]
    _line(primitives,"cost_baseline",[[-2.5,plot_baseline,0],[2.5,plot_baseline,0]],QUIET)
    _line(primitives,"optical_cost_curve",[plot(q) for q in qs],AMBER)
    _sphere(primitives,"trial_cost_point",plot(trial),.075,PINK)
    _sphere(primitives,"minimum_cost_point",plot(optimum),.075,MINT)
    theta1=asin(optimum/hypot(optimum,height))
    theta2=asin((span-optimum)/hypot(span-optimum,depth))
    return primitives, [
        _metric("trial_cost","Trial optical travel cost",trial_cost,"c=1 units"),
        _metric("minimum_cost","Minimum optical travel cost",optimum_cost,"c=1 units"),
        _metric("excess","Trial cost above minimum",max(0,trial_cost-optimum_cost)),
        _metric("snell","Snell / stationary residual",abs(derivative(optimum)),"","|n₁sin θ₁−n₂sin θ₂|; angles measured from the interface normal."),
        _metric("crossing","Optimal crossing q/d",optimum/span),
    ], {}, {"n1":n1,"n2":n2,"source_height":height,"target_depth":depth,"span":span,
            "trial_crossing":trial,"optimal_crossing":optimum,"straight_crossing":straight,
            "trial_cost":trial_cost,"minimum_cost":optimum_cost,"straight_cost":straight_cost,
            "trial_derivative":derivative(trial),"minimum_derivative":derivative(optimum),
            "minimum_second_derivative":second(optimum),"theta1_radians":theta1,"theta2_radians":theta2,
            "snell_residual":abs(n1*sin(theta1)-n2*sin(theta2)),
            "geometric_straight_length":hypot(span,height+depth),
            "optimum_geometric_length":hypot(optimum,height)+hypot(span-optimum,depth),
            "cost_crossings":qs,"cost_values":costs,
            "cost_plot_baseline":plot_baseline,"cost_plot_width":5.,"cost_plot_vertical_scale":1.,
            "bisection_iterations":70}, [
        "Refractive indices are positive relative indices n≥1, and vacuum speed is normalized to one. Optical cost is Σnᵢ·lengthᵢ, proportional to physical travel time.",
        "Cyan is the globally shortest geometric segment between the fixed points. Mint minimizes optical cost over paths crossing this flat interface once; these optimize different quantities when indices differ.",
        "T″(q)=n₁h₁²/(q²+h₁²)^(3/2)+n₂h₂²/((d−q)²+h₂²)^(3/2)>0. Endpoint derivatives have opposite signs, so this bounded family has one interior minimizer, located by derivative bisection rather than sampled argmin.",
        "The lower cost plot has its own q axis mapped to width five and plots T−Tmin above a declared baseline placed below the physical rays, without vertical rescaling. It is not part of the physical ray geometry.",
        "This fixed-source/fixed-target transmission problem does not prescribe an arbitrary incident ray. It therefore does not demonstrate a total-internal-reflection cutoff. Fermat's principle outside this convex family is a stationary-path principle, not universally a shortest-time rule."]


MODELS={"aliasing":_aliasing,"heat":_heat,"refraction":_refraction}
