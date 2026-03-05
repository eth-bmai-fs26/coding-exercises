import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import * as d3 from 'd3';

const FONT_STYLE = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');
`;

// ─── Math helpers ─────────────────────────────────────────────────────────────

function uniformSample(lo, hi) {
  return lo + Math.random() * (hi - lo);
}

function gaussianPDF(x, sigma) {
  const s2 = sigma * sigma;
  return (1 / Math.sqrt(2 * Math.PI * s2)) * Math.exp(-(x * x) / (2 * s2));
}

function generatePanel1Samples(n, count = 500) {
  return Array.from({ length: count }, () => {
    let s = 0;
    for (let i = 0; i < n; i++) s += uniformSample(-1, 1);
    return s / Math.sqrt(n / 3);
  });
}

function generatePanel2Samples(spread, count = 500) {
  const n = 20;
  return Array.from({ length: count }, () => {
    let s = 0;
    for (let i = 0; i < n; i++) s += uniformSample(-spread, spread);
    return s / Math.sqrt(n / 3);
  });
}

function generatePanel3Samples(spreadA, spreadB, count = 500) {
  const n = 20;
  const samplesA = Array.from({ length: count }, () => {
    let s = 0;
    for (let i = 0; i < n; i++) s += uniformSample(-spreadA, spreadA);
    return s / Math.sqrt(n / 3);
  });
  const samplesB = Array.from({ length: count }, () => {
    let s = 0;
    for (let i = 0; i < n; i++) s += uniformSample(-spreadB, spreadB);
    return s / Math.sqrt(n / 3);
  });
  const samplesSum = samplesA.map((a, i) => a + samplesB[i]);
  return { samplesA, samplesB, samplesSum };
}

// ─── Histogram component ──────────────────────────────────────────────────────

const NUM_BINS = 45;
const X_RANGE = [-6, 6];

function buildBins(samples) {
  const scale = d3.scaleLinear().domain(X_RANGE);
  const thresholds = d3.range(NUM_BINS + 1).map(i => X_RANGE[0] + i * (X_RANGE[1] - X_RANGE[0]) / NUM_BINS);
  const hist = d3.bin().domain(X_RANGE).thresholds(thresholds)(samples);
  return hist;
}

function Histogram({ samples, sigma, color, overlayColor, width = 520, height = 220, showSpreadShading, spread }) {
  const svgRef = useRef(null);

  const bins = useMemo(() => buildBins(samples), [samples]);

  useEffect(() => {
    if (!svgRef.current) return;
    const margin = { top: 16, right: 16, bottom: 32, left: 40 };
    const W = width - margin.left - margin.right;
    const H = height - margin.top - margin.bottom;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

    // Axes
    const xScale = d3.scaleLinear().domain(X_RANGE).range([0, W]);
    const binWidth = xScale(bins[0]?.x1 ?? 1) - xScale(bins[0]?.x0 ?? 0);
    const totalCount = samples.length || 1;
    const binWidthVal = (X_RANGE[1] - X_RANGE[0]) / NUM_BINS;
    const maxDensity = d3.max(bins, d => d.length / (totalCount * binWidthVal)) || 1;
    const theoreticalMax = gaussianPDF(0, sigma);
    const yMax = Math.max(maxDensity, theoreticalMax) * 1.15;
    const yScale = d3.scaleLinear().domain([0, yMax]).range([H, 0]);

    // Spread shading
    if (showSpreadShading && spread) {
      const x0 = xScale(-spread);
      const x1 = xScale(spread);
      g.append('rect')
        .attr('x', x0)
        .attr('width', x1 - x0)
        .attr('y', 0)
        .attr('height', H)
        .attr('fill', color)
        .attr('opacity', 0.08);

      // Arrows for spread
      const arrowY = H + 22;
      const midX = xScale(0);
      [[x0, midX - 4], [x1, midX + 4]].forEach(([fromX, toX], i) => {
        g.append('line')
          .attr('x1', fromX).attr('y1', arrowY - 10)
          .attr('x2', toX).attr('y2', arrowY - 10)
          .attr('stroke', color).attr('stroke-width', 1.5)
          .attr('marker-end', 'url(#arrowhead)');
      });
    }

    // Arrowhead marker
    svg.append('defs').append('marker')
      .attr('id', 'arrowhead')
      .attr('markerWidth', 6).attr('markerHeight', 6)
      .attr('refX', 5).attr('refY', 3)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,0 L0,6 L6,3 z')
      .attr('fill', color);

    // Bars
    g.selectAll('.bar')
      .data(bins)
      .enter()
      .append('rect')
      .attr('class', 'bar')
      .attr('x', d => xScale(d.x0) + 0.5)
      .attr('width', Math.max(0, binWidth - 1))
      .attr('y', H)
      .attr('height', 0)
      .attr('fill', color)
      .attr('opacity', 0.65)
      .attr('rx', 1)
      .transition()
      .duration(300)
      .attr('y', d => yScale(d.length / (totalCount * binWidthVal)))
      .attr('height', d => H - yScale(d.length / (totalCount * binWidthVal)));

    // Overlay Gaussian curve
    const curvePoints = d3.range(200).map(i => {
      const x = X_RANGE[0] + i * (X_RANGE[1] - X_RANGE[0]) / 199;
      return [xScale(x), yScale(gaussianPDF(x, sigma))];
    });

    const lineGen = d3.line().x(d => d[0]).y(d => d[1]).curve(d3.curveCatmullRom);
    g.append('path')
      .datum(curvePoints)
      .attr('d', lineGen)
      .attr('fill', 'none')
      .attr('stroke', overlayColor || color)
      .attr('stroke-width', 2.5)
      .attr('opacity', 0.7);

    // X axis
    g.append('g')
      .attr('transform', `translate(0,${H})`)
      .call(d3.axisBottom(xScale).ticks(7).tickSize(3))
      .call(ax => ax.select('.domain').attr('stroke', '#aaa'))
      .call(ax => ax.selectAll('.tick line').attr('stroke', '#ccc'))
      .call(ax => ax.selectAll('.tick text').style('font-size', '10px').style('font-family', 'DM Sans, sans-serif').attr('fill', '#666'));

    // Y axis
    g.append('g')
      .call(d3.axisLeft(yScale).ticks(4).tickSize(3))
      .call(ax => ax.select('.domain').attr('stroke', '#aaa'))
      .call(ax => ax.selectAll('.tick line').attr('stroke', '#ccc'))
      .call(ax => ax.selectAll('.tick text').style('font-size', '10px').style('font-family', 'DM Sans, sans-serif').attr('fill', '#666'));

    // X label
    g.append('text')
      .attr('x', W / 2)
      .attr('y', H + 28)
      .attr('text-anchor', 'middle')
      .style('font-size', '11px')
      .style('font-family', 'DM Sans, sans-serif')
      .attr('fill', '#888')
      .text('value');

  }, [samples, sigma, color, overlayColor, width, height, bins, showSpreadShading, spread]);

  return (
    <svg
      ref={svgRef}
      width={width}
      height={height}
      style={{ display: 'block' }}
    />
  );
}

// ─── Right-triangle SVG ───────────────────────────────────────────────────────

function PythagoreanTriangle({ a, b, size = 200 }) {
  const SCALE = 45;
  const legA = a * SCALE;
  const legB = b * SCALE;
  const hyp = Math.sqrt(a * a + b * b);
  const legH = hyp * SCALE;
  const pad = 32;
  const W = legB + pad * 2 + 40;
  const H = legA + pad * 2 + 20;

  // Triangle points: right angle at bottom-left
  const x0 = pad, y0 = pad + legA;
  const x1 = pad, y1 = pad;
  const x2 = pad + legB, y2 = pad + legA;

  return (
    <svg width={W} height={H} style={{ display: 'block', margin: '0 auto' }}>
      {/* Triangle fill */}
      <polygon
        points={`${x0},${y0} ${x1},${y1} ${x2},${y2}`}
        fill="#e8dff5"
        stroke="#7B5EA7"
        strokeWidth="2"
      />

      {/* Right-angle marker */}
      <polyline
        points={`${x0 + 10},${y0 - 0} ${x0 + 10},${y0 - 10} ${x0 + 0},${y0 - 10}`}
        fill="none"
        stroke="#7B5EA7"
        strokeWidth="1.5"
      />

      {/* Label for leg A (vertical, left side) */}
      <text
        x={x0 - 12}
        y={(y0 + y1) / 2}
        textAnchor="middle"
        dominantBaseline="middle"
        fill="#E07A5F"
        fontSize="13"
        fontFamily="DM Sans, sans-serif"
        fontWeight="600"
      >
        A={a.toFixed(1)}
      </text>

      {/* Label for leg B (horizontal, bottom side) */}
      <text
        x={(x0 + x2) / 2}
        y={y2 + 18}
        textAnchor="middle"
        dominantBaseline="middle"
        fill="#3D85C6"
        fontSize="13"
        fontFamily="DM Sans, sans-serif"
        fontWeight="600"
      >
        B={b.toFixed(1)}
      </text>

      {/* Label for hypotenuse */}
      <text
        x={(x1 + x2) / 2 + 14}
        y={(y1 + y2) / 2 - 8}
        textAnchor="middle"
        dominantBaseline="middle"
        fill="#7B5EA7"
        fontSize="13"
        fontFamily="DM Sans, sans-serif"
        fontWeight="600"
      >
        √(A²+B²)≈{hyp.toFixed(2)}
      </text>
    </svg>
  );
}

// ─── Panel 1 ──────────────────────────────────────────────────────────────────

function Panel1() {
  const [n, setN] = useState(1);
  const [samples, setSamples] = useState([]);
  const [animating, setAnimating] = useState(false);

  const caption = useMemo(() => {
    if (n === 1) return "With just 1 draw, every value is equally likely — a flat shape.";
    if (n <= 3) return "Already starting to pile up in the middle...";
    if (n <= 9) return "Looking more and more like a bell!";
    return "That's a bell curve! This is what a Gaussian distribution looks like.";
  }, [n]);

  const handleDraw = useCallback(() => {
    if (animating) return;
    setAnimating(true);
    setSamples([]);
    const all = generatePanel1Samples(n, 500);
    const BATCHES = 10;
    const BATCH_SIZE = 50;
    let batch = 0;
    const timer = setInterval(() => {
      batch++;
      setSamples(all.slice(0, batch * BATCH_SIZE));
      if (batch >= BATCHES) {
        clearInterval(timer);
        setAnimating(false);
      }
    }, 90);
  }, [n, animating]);

  return (
    <div style={{ fontFamily: 'DM Sans, sans-serif' }}>
      <h2 style={{ fontFamily: 'DM Serif Display, serif', fontSize: '1.6rem', color: '#3a2a1e', marginBottom: '0.25rem' }}>
        What is a Bell Curve?
      </h2>
      <p style={{ color: '#666', marginBottom: '1.25rem', maxWidth: 580, lineHeight: 1.6 }}>
        Here's a surprising fact: if you add up many small random numbers, you always
        get a bell-shaped result — no matter where those numbers come from. Try it yourself!
      </p>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
        <label style={{ fontWeight: 500, color: '#3a2a1e', whiteSpace: 'nowrap' }}>
          How many random numbers to add up:&nbsp;
          <span style={{ color: '#E07A5F', fontWeight: 700, fontSize: '1.1em' }}>{n}</span>
        </label>
        <input
          type="range" min={1} max={30} value={n}
          onChange={e => { setN(Number(e.target.value)); setSamples([]); }}
          style={{ width: 180, accentColor: '#E07A5F' }}
        />
      </div>

      <button
        onClick={handleDraw}
        disabled={animating}
        style={{
          background: animating ? '#ccc' : '#E07A5F',
          color: 'white',
          border: 'none',
          borderRadius: 8,
          padding: '10px 24px',
          fontSize: '1rem',
          fontFamily: 'DM Sans, sans-serif',
          fontWeight: 600,
          cursor: animating ? 'not-allowed' : 'pointer',
          marginBottom: '1.5rem',
          transition: 'background 0.2s',
        }}
      >
        {animating ? 'Drawing samples...' : 'Draw 500 samples'}
      </button>

      <div style={{ background: 'white', borderRadius: 12, boxShadow: '0 2px 12px rgba(0,0,0,0.07)', padding: '1rem', display: 'inline-block' }}>
        <Histogram
          samples={samples}
          sigma={1}
          color="#E07A5F"
          width={560}
          height={240}
        />
      </div>

      <div style={{
        marginTop: '1rem',
        padding: '0.75rem 1rem',
        background: '#fff8f5',
        borderLeft: '3px solid #E07A5F',
        borderRadius: 4,
        maxWidth: 560,
        color: '#3a2a1e',
        fontStyle: 'italic',
        lineHeight: 1.6,
      }}>
        {caption}
      </div>
    </div>
  );
}

// ─── Panel 2 ──────────────────────────────────────────────────────────────────

function Panel2() {
  const [spread, setSpread] = useState(1.0);
  const [samples, setSamples] = useState([]);
  const [animating, setAnimating] = useState(false);

  const handleDraw = useCallback(() => {
    if (animating) return;
    setAnimating(true);
    setSamples([]);
    const all = generatePanel2Samples(spread, 500);
    const BATCHES = 10;
    const BATCH_SIZE = 50;
    let batch = 0;
    const timer = setInterval(() => {
      batch++;
      setSamples(all.slice(0, batch * BATCH_SIZE));
      if (batch >= BATCHES) {
        clearInterval(timer);
        setAnimating(false);
      }
    }, 90);
  }, [spread, animating]);

  return (
    <div style={{ fontFamily: 'DM Sans, sans-serif' }}>
      <h2 style={{ fontFamily: 'DM Serif Display, serif', fontSize: '1.6rem', color: '#3a2a1e', marginBottom: '0.25rem' }}>
        Changing the Spread
      </h2>
      <p style={{ color: '#666', marginBottom: '1.25rem', maxWidth: 580, lineHeight: 1.6 }}>
        Every bell curve has a "spread" — how wide or narrow it is.
        Drag the slider to change the spread and watch what happens.
      </p>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
        <label style={{ fontWeight: 500, color: '#3a2a1e', whiteSpace: 'nowrap' }}>
          Spread:&nbsp;
          <span style={{ color: '#E07A5F', fontWeight: 700, fontSize: '1.1em' }}>{spread.toFixed(1)}</span>
        </label>
        <input
          type="range" min={0.5} max={3.0} step={0.1} value={spread}
          onChange={e => { setSpread(Number(e.target.value)); setSamples([]); }}
          style={{ width: 200, accentColor: '#E07A5F' }}
        />
      </div>

      <button
        onClick={handleDraw}
        disabled={animating}
        style={{
          background: animating ? '#ccc' : '#E07A5F',
          color: 'white',
          border: 'none',
          borderRadius: 8,
          padding: '10px 24px',
          fontSize: '1rem',
          fontFamily: 'DM Sans, sans-serif',
          fontWeight: 600,
          cursor: animating ? 'not-allowed' : 'pointer',
          marginBottom: '1.5rem',
          transition: 'background 0.2s',
        }}
      >
        {animating ? 'Drawing samples...' : 'Draw 500 samples'}
      </button>

      <div style={{ background: 'white', borderRadius: 12, boxShadow: '0 2px 12px rgba(0,0,0,0.07)', padding: '1rem', display: 'inline-block' }}>
        <Histogram
          samples={samples}
          sigma={spread}
          color="#E07A5F"
          width={560}
          height={240}
          showSpreadShading
          spread={spread}
        />
      </div>

      <div style={{
        marginTop: '1rem',
        padding: '0.75rem 1rem',
        background: '#fff8f5',
        borderLeft: '3px solid #E07A5F',
        borderRadius: 4,
        maxWidth: 560,
        color: '#3a2a1e',
        lineHeight: 1.6,
      }}>
        A <strong>wider spread</strong> means the bell curve is wider and flatter.
        A <strong>narrower spread</strong> means values cluster more tightly around zero.
        The shaded region shows the spread distance from the center.
      </div>
    </div>
  );
}

// ─── Panel 3 ──────────────────────────────────────────────────────────────────

function Panel3() {
  const [spreadA, setSpreadA] = useState(1.0);
  const [spreadB, setSpreadB] = useState(1.0);
  const [samplesA, setSamplesA] = useState([]);
  const [samplesB, setSamplesB] = useState([]);
  const [samplesSum, setSamplesSum] = useState([]);
  const [animating, setAnimating] = useState(false);
  const [showInsight, setShowInsight] = useState(false);

  const predictedSpread = Math.sqrt(spreadA * spreadA + spreadB * spreadB);

  const handleDraw = useCallback(() => {
    if (animating) return;
    setAnimating(true);
    setSamplesA([]); setSamplesB([]); setSamplesSum([]);
    const { samplesA: allA, samplesB: allB, samplesSum: allSum } = generatePanel3Samples(spreadA, spreadB, 500);
    const BATCHES = 10;
    const BATCH_SIZE = 50;
    let batch = 0;
    const timer = setInterval(() => {
      batch++;
      setSamplesA(allA.slice(0, batch * BATCH_SIZE));
      setSamplesB(allB.slice(0, batch * BATCH_SIZE));
      setSamplesSum(allSum.slice(0, batch * BATCH_SIZE));
      if (batch >= BATCHES) {
        clearInterval(timer);
        setAnimating(false);
      }
    }, 90);
  }, [spreadA, spreadB, animating]);

  const histW = 380;
  const histH = 190;

  return (
    <div style={{ fontFamily: 'DM Sans, sans-serif' }}>
      <h2 style={{ fontFamily: 'DM Serif Display, serif', fontSize: '1.6rem', color: '#3a2a1e', marginBottom: '0.25rem' }}>
        Adding Two Bell Curves
      </h2>
      <p style={{ color: '#666', marginBottom: '1.25rem', maxWidth: 680, lineHeight: 1.6 }}>
        What happens when you take a sample from one bell curve and add it to a sample
        from another? You get a <em>new</em> bell curve — and its spread follows the
        Pythagorean theorem!
      </p>

      <div style={{ display: 'flex', gap: '2.5rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <label style={{ fontWeight: 500, color: '#3a2a1e', whiteSpace: 'nowrap' }}>
            <span style={{ color: '#E07A5F', fontWeight: 700 }}>Spread A:</span>&nbsp;
            <span style={{ color: '#E07A5F', fontWeight: 700, fontSize: '1.1em' }}>{spreadA.toFixed(1)}</span>
          </label>
          <input
            type="range" min={0.5} max={3.0} step={0.1} value={spreadA}
            onChange={e => { setSpreadA(Number(e.target.value)); setSamplesA([]); setSamplesSum([]); }}
            style={{ width: 160, accentColor: '#E07A5F' }}
          />
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <label style={{ fontWeight: 500, color: '#3a2a1e', whiteSpace: 'nowrap' }}>
            <span style={{ color: '#3D85C6', fontWeight: 700 }}>Spread B:</span>&nbsp;
            <span style={{ color: '#3D85C6', fontWeight: 700, fontSize: '1.1em' }}>{spreadB.toFixed(1)}</span>
          </label>
          <input
            type="range" min={0.5} max={3.0} step={0.1} value={spreadB}
            onChange={e => { setSpreadB(Number(e.target.value)); setSamplesB([]); setSamplesSum([]); }}
            style={{ width: 160, accentColor: '#3D85C6' }}
          />
        </div>
      </div>

      <button
        onClick={handleDraw}
        disabled={animating}
        style={{
          background: animating ? '#ccc' : '#7B5EA7',
          color: 'white',
          border: 'none',
          borderRadius: 8,
          padding: '10px 24px',
          fontSize: '1rem',
          fontFamily: 'DM Sans, sans-serif',
          fontWeight: 600,
          cursor: animating ? 'not-allowed' : 'pointer',
          marginBottom: '1.75rem',
          transition: 'background 0.2s',
        }}
      >
        {animating ? 'Drawing samples...' : 'Draw 500 samples'}
      </button>

      {/* Three histograms */}
      <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap', alignItems: 'flex-start', marginBottom: '2rem' }}>
        <div>
          <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#E07A5F', marginBottom: 4, textAlign: 'center' }}>
            Bell Curve A &nbsp;(spread {spreadA.toFixed(1)})
          </div>
          <div style={{ background: 'white', borderRadius: 10, boxShadow: '0 2px 10px rgba(0,0,0,0.07)', padding: '0.75rem' }}>
            <Histogram samples={samplesA} sigma={spreadA} color="#E07A5F" width={histW} height={histH} />
          </div>
        </div>
        <div>
          <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#3D85C6', marginBottom: 4, textAlign: 'center' }}>
            Bell Curve B &nbsp;(spread {spreadB.toFixed(1)})
          </div>
          <div style={{ background: 'white', borderRadius: 10, boxShadow: '0 2px 10px rgba(0,0,0,0.07)', padding: '0.75rem' }}>
            <Histogram samples={samplesB} sigma={spreadB} color="#3D85C6" width={histW} height={histH} />
          </div>
        </div>
        <div>
          <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#7B5EA7', marginBottom: 4, textAlign: 'center' }}>
            A + B &nbsp;(predicted spread {predictedSpread.toFixed(2)})
          </div>
          <div style={{ background: 'white', borderRadius: 10, boxShadow: '0 2px 10px rgba(0,0,0,0.07)', padding: '0.75rem' }}>
            <Histogram samples={samplesSum} sigma={predictedSpread} color="#7B5EA7" width={histW} height={histH} />
          </div>
        </div>
      </div>

      {/* Pythagorean triangle */}
      <div style={{
        background: 'white',
        borderRadius: 12,
        boxShadow: '0 2px 12px rgba(0,0,0,0.07)',
        padding: '1.25rem 1.5rem',
        maxWidth: 520,
        marginBottom: '1.25rem',
      }}>
        <div style={{ fontFamily: 'DM Serif Display, serif', fontSize: '1.1rem', color: '#3a2a1e', marginBottom: '0.75rem' }}>
          The Pythagorean Theorem of Spread
        </div>
        <PythagoreanTriangle a={spreadA} b={spreadB} />
        <div style={{ textAlign: 'center', marginTop: 8, color: '#555', fontSize: '0.95rem', lineHeight: 1.5 }}>
          <strong style={{ color: '#E07A5F' }}>A²</strong> +{' '}
          <strong style={{ color: '#3D85C6' }}>B²</strong> ={' '}
          <strong style={{ color: '#7B5EA7' }}>({predictedSpread.toFixed(2)})²</strong>
          <br />
          <span style={{ fontSize: '0.85rem', color: '#888' }}>
            {spreadA.toFixed(1)}² + {spreadB.toFixed(1)}² = {(spreadA * spreadA + spreadB * spreadB).toFixed(2)} → spread = {predictedSpread.toFixed(2)}
          </span>
        </div>
      </div>

      <div style={{
        padding: '0.75rem 1rem',
        background: '#f3effe',
        borderLeft: '3px solid #7B5EA7',
        borderRadius: 4,
        maxWidth: 580,
        color: '#3a2a1e',
        lineHeight: 1.6,
        marginBottom: '0.75rem',
      }}>
        <strong>The spread of the sum follows the Pythagorean theorem!</strong>{' '}
        Just like the hypotenuse of a right triangle, the combined spread is
        √(A² + B²) — always larger than either A or B alone, but less than A + B.
      </div>

      <button
        onClick={() => setShowInsight(v => !v)}
        style={{
          background: 'transparent',
          border: '1.5px solid #7B5EA7',
          color: '#7B5EA7',
          borderRadius: 8,
          padding: '7px 18px',
          fontSize: '0.9rem',
          fontFamily: 'DM Sans, sans-serif',
          fontWeight: 500,
          cursor: 'pointer',
        }}
      >
        {showInsight ? 'Hide insight' : 'Why does this work? ▾'}
      </button>

      {showInsight && (
        <div style={{
          marginTop: '0.75rem',
          padding: '1rem 1.25rem',
          background: '#faf7ff',
          border: '1px solid #d5c8f0',
          borderRadius: 8,
          maxWidth: 580,
          color: '#3a2a1e',
          lineHeight: 1.7,
          fontSize: '0.95rem',
        }}>
          Each sample of A is built from 20 small random draws. Each sample of B is
          built from 20 different small random draws. When we add them, we're really
          adding <em>pairs</em> — one draw from A's range and one from B's range.
          The combined spread of each pair is A² + B², so the total spread across
          all pairs is √(A² + B²). That's exactly the Pythagorean theorem!
        </div>
      )}
    </div>
  );
}

// ─── Main App ─────────────────────────────────────────────────────────────────

const TABS = [
  { id: 'panel1', label: '1. What is a Bell Curve?' },
  { id: 'panel2', label: '2. Changing the Spread' },
  { id: 'panel3', label: '3. Adding Two Bell Curves' },
];

export default function GaussianVisualizer() {
  const [activeTab, setActiveTab] = useState('panel1');

  return (
    <>
      <style>{FONT_STYLE}</style>
      <div style={{
        minHeight: '100vh',
        background: '#FDFBF7',
        fontFamily: 'DM Sans, sans-serif',
        padding: '0 0 60px 0',
      }}>
        {/* Header */}
        <div style={{
          background: 'white',
          borderBottom: '1px solid #e8e2d9',
          padding: '1.5rem 2rem 0 2rem',
          maxWidth: 1200,
          margin: '0 auto',
        }}>
          <h1 style={{
            fontFamily: 'DM Serif Display, serif',
            fontSize: '2rem',
            color: '#2a1e14',
            margin: 0,
            marginBottom: '0.2rem',
          }}>
            The Shape of Randomness
          </h1>
          <p style={{ color: '#888', margin: '0 0 1.25rem 0', fontSize: '0.95rem' }}>
            An interactive tour of bell curves — no math required.
          </p>

          {/* Tabs */}
          <div style={{ display: 'flex', gap: 0, borderTop: '1px solid #e8e2d9', marginLeft: -8 }}>
            {TABS.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  borderBottom: activeTab === tab.id ? '3px solid #E07A5F' : '3px solid transparent',
                  color: activeTab === tab.id ? '#E07A5F' : '#888',
                  fontFamily: 'DM Sans, sans-serif',
                  fontWeight: activeTab === tab.id ? 600 : 400,
                  fontSize: '0.95rem',
                  padding: '0.85rem 1.25rem',
                  cursor: 'pointer',
                  transition: 'color 0.15s, border-color 0.15s',
                  whiteSpace: 'nowrap',
                }}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Panel content */}
        <div style={{ maxWidth: 1200, margin: '0 auto', padding: '2rem 2rem 0 2rem' }}>
          {activeTab === 'panel1' && <Panel1 />}
          {activeTab === 'panel2' && <Panel2 />}
          {activeTab === 'panel3' && <Panel3 />}
        </div>
      </div>
    </>
  );
}
