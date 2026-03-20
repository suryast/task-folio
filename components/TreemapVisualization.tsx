'use client'

import { useEffect, useRef } from 'react'
import * as d3 from 'd3'
import { useRouter } from 'next/navigation'

interface Occupation {
  anzsco_code: string
  title: string
  employment: number
  median_pay_aud: number
  ai_exposure: number
  outlook: string
  source: string
}

interface TreemapProps {
  occupations: Occupation[]
}

export function TreemapVisualization({ occupations }: TreemapProps) {
  const svgRef = useRef<SVGSVGElement>(null)
  const router = useRouter()

  useEffect(() => {
    if (!svgRef.current || occupations.length === 0) return

    // Clear previous render
    d3.select(svgRef.current).selectAll('*').remove()

    const width = 1200
    const height = 800
    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', `0 0 ${width} ${height}`)
      .attr('style', 'max-width: 100%; height: auto;')

    // Prepare hierarchical data
    const root = d3.hierarchy({
      name: 'root',
      children: occupations.map(occ => ({
        name: occ.title,
        value: occ.employment || 1,
        data: occ
      }))
    })
      .sum(d => (d as any).value || 0)
      .sort((a, b) => (b.value || 0) - (a.value || 0))

    // Create treemap layout
    const treemap = d3.treemap<any>()
      .size([width, height])
      .paddingInner(2)
      .paddingOuter(4)
      .round(true)

    treemap(root)

    // Color scale based on AI exposure (0-1)
    const colorScale = d3.scaleSequential(d3.interpolateRdYlGn)
      .domain([1, 0]) // Reversed: high exposure = red, low = green

    // Create cells
    const cell = svg.selectAll('g')
      .data(root.leaves())
      .join('g')
      .attr('transform', d => `translate(${d.x0},${d.y0})`)
      .style('cursor', 'pointer')
      .on('click', (event, d: any) => {
        const code = d.data.data.anzsco_code
        router.push(`/occupations/${code}`)
      })

    // Add rectangles
    cell.append('rect')
      .attr('width', d => d.x1 - d.x0)
      .attr('height', d => d.y1 - d.y0)
      .attr('fill', (d: any) => {
        const exposure = d.data.data.ai_exposure || 0
        return colorScale(exposure)
      })
      .attr('stroke', '#fff')
      .attr('stroke-width', 1)
      .on('mouseenter', function() {
        d3.select(this)
          .attr('stroke', '#000')
          .attr('stroke-width', 2)
      })
      .on('mouseleave', function() {
        d3.select(this)
          .attr('stroke', '#fff')
          .attr('stroke-width', 1)
      })

    // Add text labels (only if cell is large enough)
    cell.append('text')
      .attr('x', 4)
      .attr('y', 14)
      .attr('font-size', (d: any) => {
        const width = d.x1 - d.x0
        const height = d.y1 - d.y0
        return Math.min(width / 6, height / 3, 11)
      })
      .attr('fill', '#000')
      .attr('opacity', 0.8)
      .attr('pointer-events', 'none')
      .text((d: any) => {
        const width = d.x1 - d.x0
        const height = d.y1 - d.y0
        // Only show text if cell is large enough
        if (width < 60 || height < 30) return ''
        return d.data.name
      })
      .each(function(d: any) {
        const self = d3.select(this)
        const width = d.x1 - d.x0
        const text = self.text()
        if (text.length * 6 > width - 8) {
          self.text(text.substring(0, Math.floor(width / 6) - 3) + '...')
        }
      })

    // Add title tooltips
    cell.append('title')
      .text((d: any) => {
        const occ = d.data.data
        return `${occ.title}\n` +
               `Employment: ${(occ.employment || 0).toLocaleString()}\n` +
               `AI Exposure: ${((occ.ai_exposure || 0) * 100).toFixed(0)}%\n` +
               `Median Pay: $${(occ.median_pay_aud || 0).toLocaleString()}`
      })

  }, [occupations, router])

  return (
    <div className="rounded-lg bg-white p-4 shadow-lg dark:bg-zinc-900">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
          Australian Occupations by Employment
        </h2>
        <div className="flex items-center gap-4 text-xs text-zinc-600 dark:text-zinc-400">
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-sm bg-green-500"></div>
            <span>Low AI Impact</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-sm bg-red-500"></div>
            <span>High AI Impact</span>
          </div>
        </div>
      </div>
      <svg ref={svgRef}></svg>
    </div>
  )
}
