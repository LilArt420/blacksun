// black-sun: the sky during the Black Sun instance.
//
// The server says how far the Black Sun has risen with `@@event bs_sky <n> <stage>`
// (npc/black_sun.txt, on every map load of the run's maps and whenever either
// changes): 0 dawn, 1 dusk, 2 rising, 3 the full eclipse; <stage> is the run's
// stage (0-12), and the Black Sun travels across the sky faster at every one. One light full-screen
// pass grades the picture towards a cold, blood-red dark and hangs the Black
// Sun -- a black disc in a burning corona -- in the upper part of the screen.
// It eases between stages. It is on only after the server's word on the
// current map (the run's Niflheim copy has the real field's name), and goes
// off the moment the map changes.

const FRAGMENT = `
uniform float uLevel;	// 0..3, eased
uniform float uPhase;	// how far the Black Sun has travelled (radians)

void main() {
	vec3 color = texture(uTexture, vUv).rgb;
	float dusk = clamp(uLevel, 0.0, 1.0);
	float rise = clamp(uLevel - 1.0, 0.0, 1.0);
	float full = clamp(uLevel - 2.0, 0.0, 1.0);

	// grade: darker, colder, then bled red as the eclipse comes
	float luma = dot(color, vec3(0.299, 0.587, 0.114));
	vec3 night = mix(color, vec3(luma) * vec3(0.55, 0.6, 0.85), 0.35 * dusk);
	night *= 1.0 - 0.12 * dusk - 0.08 * rise - 0.08 * full;
	night = mix(night, vec3(luma * 0.9, luma * 0.22, luma * 0.2), 0.16 * rise + 0.18 * full);

	// a red vignette that tightens with the eclipse
	vec2 c = vUv - 0.5;
	float vig = smoothstep(0.35, 0.85, length(c * vec2(1.2, 1.0)));
	night = mix(night, night * vec3(0.55, 0.05, 0.04), vig * (0.3 * rise + 0.35 * full));

	// the Black Sun, high on the screen: it drifts slowly, breathes, and its
	// corona burns -- a bright ring at the edge, turning streamers, a wide glow
	float aspect = uResolution.x / uResolution.y;
	vec2 center = vec2(0.52 + 0.22 * sin(uPhase), 0.83 + 0.03 * sin(uPhase * 2.0 + 0.7))
		+ vec2(0.006 * sin(uTime * 0.37), 0.004 * sin(uTime * 0.29));
	vec2 p = vec2((vUv.x - center.x) * aspect, vUv.y - center.y);
	float d = length(p);
	float ang = atan(p.y, p.x);
	float size = (0.045 + 0.02 * full) * (1.0 + 0.04 * sin(uTime * 0.9) + 0.02 * sin(uTime * 2.3));
	if (rise > 0.0) {
		float pulse = 0.82 + 0.18 * sin(uTime * 1.3) + 0.06 * sin(uTime * 3.7);
		float rays = 0.55 + 0.45 * sin(ang * 9.0 + uTime * 0.35) * sin(ang * 5.0 - uTime * 0.22 + 1.7);
		rays = pow(max(rays, 0.0), 1.5);
		float r = max(d - size, 0.0);
		float rim = exp(-r * 90.0);
		float corona = exp(-r * (14.0 - 6.0 * rays));
		float halo = 0.22 * exp(-r * 4.5) * (1.0 - smoothstep(0.3, 0.7, d));
		vec3 hot = mix(vec3(1.0, 0.75, 0.35), vec3(1.0, 0.25, 0.08), full);
		vec3 deep = mix(vec3(0.95, 0.35, 0.08), vec3(0.75, 0.02, 0.02), full);
		vec3 glow = hot * rim * 1.4 + deep * corona * (0.6 + 0.4 * rays) + deep * halo;
		night += glow * step(size, d) * pulse * (0.5 * rise + 0.6 * full);
		// the disc: black, with a faint red sheen crawling over it at the eclipse
		float disc = 1.0 - smoothstep(size - 0.003, size, d);
		float sheen = 0.06 * full * (0.5 + 0.5 * sin(p.x * 60.0 + uTime * 0.6)) * smoothstep(size * 0.4, size, d);
		night = mix(night, vec3(sheen, 0.0, 0.0), disc * rise);
	}
	fragColor = vec4(night, 1.0);
}
`;

export default function init(params, api) {
	if (api?.version !== 1) throw new Error('black-sun needs client API 1');
	if (!api.graphics?.supported()) {
		console.warn('[black-sun] this client cannot run graphics passes; no Black Sun sky');
		return;
	}
	let here = false;	// the server has spoken for this map
	let target = 0;
	let level = 0;
	let stage = 0;
	let speed = 0;		// radians a second, eased towards the stage's
	let phase = 0;
	let last = performance.now();
	// how fast the Black Sun travels at each stage of the run: faster every time
	const SPEED = [0.03, 0.03, 0.04, 0.05, 0.06, 0.07, 0.085, 0.1, 0.12, 0.14, 0.17, 0.05, 0.03];

	api.on('map:leave', () => { here = false; target = 0; level = 0; });
	api.on('server:event', ({ command, text }) => {
		if (command !== 'bs_sky') return;
		const [n, st] = String(text).trim().split(/\s+/).map(Number);
		if (!Number.isFinite(n)) return;
		if (!here) level = Math.max(0, Math.min(3, n));	// a fresh map: no fade in
		here = true;
		target = Math.max(0, Math.min(3, n));
		if (Number.isFinite(st)) stage = Math.max(0, Math.min(SPEED.length - 1, Math.floor(st)));
	}, { replay: false });

	api.graphics.registerPass({
		name: 'Black Sun',
		fragment: FRAGMENT,
		uniforms: () => {
			const now = performance.now();
			const dt = Math.min(0.1, (now - last) / 1000);
			last = now;
			// a stage change takes a few seconds to come over the sky
			const step = dt * 0.4;
			level += Math.max(-step, Math.min(step, target - level));
			speed += (SPEED[stage] - speed) * Math.min(1, dt * 0.5);
			phase = (phase + speed * dt) % (Math.PI * 2000);
			return { uLevel: level, uPhase: phase };
		},
		enabled: () => here && (level > 0.01 || target > 0),
	});
}
