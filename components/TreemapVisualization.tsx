'use client'

import { useEffect, useRef, useState } from 'react'
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

interface TreemapNode extends d3.HierarchyRectangularNode<any> {
  x0: number
  y0: number
  x1: number
  y1: number
  data: {
    name: string
    value: number
    data: Occupation
    category?: string
  }
}

interface TreemapProps {
  occupations: Occupation[]
}

type SortOption = 'employment' | 'ai_exposure' | 'category' | 'disruption'

// Extract category from ANZSCO code (first digit = major group)
function getCategory(code: string): string {
  const majorGroup = code.charAt(0)
  const categories: Record<string, string> = {
    '1': 'Managers',
    '2': 'Professionals',
    '3': 'Technicians & Trades',
    '4': 'Community & Personal Service',
    '5': 'Clerical & Administrative',
    '6': 'Sales Workers',
    '7': 'Machinery Operators & Drivers',
    '8': 'Labourers',
  }
  return categories[majorGroup] || 'Other'
}

// Neobrutal color palette
const COLORS = {
  danger: '#ee8888',
  warning: '#fed170',
  success: '#97ee88',
  main: '#88d4ee',
}

export function TreemapVisualization({ occupations }: TreemapProps) {
  const svgRef = useRef<SVGSVGElement>(null)
  const router = useRouter()
  const [sortBy, setSortBy] = useState<SortOption>('category')

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

    // Prepare hierarchical data based on sort option
    let hierarchyData: any

    if (sortBy === 'category') {
      // Group by ANZSCO major category
      const grouped = d3.group(occupations, occ => getCategory(occ.anzsco_code))
      hierarchyData = {
        name: 'root',
        children: Array.from(grouped, ([category, occs]) => ({
          name: category,
          children: occs.map(occ => ({
            name: occ.title,
            value: occ.employment || 1,
            data: occ,
            category
          }))
        }))
      }
    } else if (sortBy === 'ai_exposure') {
      // Group by AI exposure severity
      const getExposureGroup = (exposure: number): string => {
        if (exposure >= 0.8) return 'Very High (80%+)'
        if (exposure >= 0.6) return 'High (60-79%)'
        if (exposure >= 0.4) return 'Medium (40-59%)'
        return 'Low (<40%)'
      }
      // Manually bucket occupations
      const buckets: Record<string, Occupation[]> = {
        'Very High (80%+)': [],
        'High (60-79%)': [],
        'Medium (40-59%)': [],
        'Low (<40%)': []
      }
      occupations.forEach(occ => {
        const group = getExposureGroup(occ.ai_exposure || 0)
        buckets[group].push(occ)
      })
      // Order from highest to lowest exposure
      const order = ['Very High (80%+)', 'High (60-79%)', 'Medium (40-59%)', 'Low (<40%)']
      hierarchyData = {
        name: 'root',
        children: order.filter(g => buckets[g].length > 0).map(group => ({
          name: group,
          children: buckets[group]
            .sort((a, b) => (b.ai_exposure || 0) - (a.ai_exposure || 0))
            .map(occ => ({
              name: occ.title,
              value: occ.employment || 1,
              data: occ,
              category: group
            }))
        }))
      }
    } else if (sortBy === 'disruption') {
      // Size by disruption impact (employment × exposure = workers affected)
      hierarchyData = {
        name: 'root',
        children: occupations.map(occ => ({
          name: occ.title,
          // Value = potential workers disrupted (employment × exposure percentage)
          value: Math.round((occ.employment || 1) * (occ.ai_exposure || 0)),
          data: occ
        }))
      }
    } else {
      // Default: flat by employment
      hierarchyData = {
        name: 'root',
        children: occupations.map(occ => ({
          name: occ.title,
          value: occ.employment || 1,
          data: occ
        }))
      }
    }

    const root = d3.hierarchy(hierarchyData)
      .sum(d => (d as any).value || 0)
      .sort((a, b) => (b.value || 0) - (a.value || 0))

    // Create treemap layout
    const treemap = d3.treemap<any>()
      .size([width, height])
      .paddingInner((sortBy === 'employment' || sortBy === 'disruption') ? 3 : 4)
      .paddingOuter(6)
      .paddingTop((sortBy === 'employment' || sortBy === 'disruption') ? 6 : 28)
      .round(true)

    treemap(root)

    // Neobrutal color scale
    const colorScale = (exposure: number): string => {
      if (exposure >= 0.7) return COLORS.danger
      if (exposure >= 0.5) return COLORS.warning
      return COLORS.success
    }

    // Get all leaf nodes
    const leaves = root.leaves() as unknown as TreemapNode[]

    // If grouped, draw category backgrounds and labels
    if (sortBy !== 'employment') {
      const groups = root.children as unknown as TreemapNode[]
      if (groups) {
        // Category backgrounds - brutal style
        // Get computed colors for dark mode support
        const strokeColor = getComputedStyle(document.documentElement).getPropertyValue('--black').trim() || '#000000'
        
        svg.selectAll('.category-bg')
          .data(groups)
          .join('rect')
          .attr('class', 'category-bg')
          .attr('x', d => d.x0)
          .attr('y', d => d.y0)
          .attr('width', d => d.x1 - d.x0)
          .attr('height', d => d.y1 - d.y0)
          .attr('fill', 'none')
          .attr('stroke', strokeColor)
          .attr('stroke-width', 2)
          .attr('rx', 5)

        // Category labels - bold brutal style
        // Get computed text color for dark mode support
        const textColor = getComputedStyle(document.documentElement).getPropertyValue('--black').trim() || '#000000'
        
        svg.selectAll('.category-label')
          .data(groups)
          .join('text')
          .attr('class', 'category-label')
          .attr('x', d => d.x0 + 8)
          .attr('y', d => d.y0 + 18)
          .attr('font-size', 13)
          .attr('font-weight', 700)
          .attr('fill', textColor)
          .text(d => (d.data as any).name.toUpperCase())
      }
    }

    // Create cells
    const cell = svg.selectAll('.cell')
      .data(leaves)
      .join('g')
      .attr('class', 'cell')
      .attr('transform', (d: TreemapNode) => `translate(${d.x0},${d.y0})`)
      .style('cursor', 'pointer')
      .on('click', (event, d: TreemapNode) => {
        const code = d.data.data.anzsco_code
        router.push(`/occupations/${code}`)
      })

    // Get computed colors for dark mode support (for cells that don't have category parents)
    const cellStrokeColor = getComputedStyle(document.documentElement).getPropertyValue('--black').trim() || '#000000'
    
    // Add rectangles - brutal style
    cell.append('rect')
      .attr('width', (d: TreemapNode) => d.x1 - d.x0)
      .attr('height', (d: TreemapNode) => d.y1 - d.y0)
      .attr('fill', (d: TreemapNode) => {
        const exposure = d.data.data.ai_exposure || 0
        return colorScale(exposure)
      })
      .attr('stroke', cellStrokeColor)
      .attr('stroke-width', 2)
      .attr('rx', 5)
      .on('mouseenter', function() {
        d3.select(this)
          .attr('stroke-width', 3)
          .attr('transform', 'translate(-2, -2)')
      })
      .on('mouseleave', function() {
        d3.select(this)
          .attr('stroke-width', 2)
          .attr('transform', null)
      })

    // Add text labels - bold style (text inside colored cells stays black for contrast)
    cell.append('text')
      .attr('x', 6)
      .attr('y', 16)
      .attr('font-size', (d: TreemapNode) => {
        const width = d.x1 - d.x0
        const height = d.y1 - d.y0
        return Math.min(width / 6, height / 3, 12)
      })
      .attr('font-weight', 600)
      .attr('fill', '#000000')  // Keep black for contrast on colored backgrounds
      .attr('pointer-events', 'none')
      .text((d: TreemapNode) => {
        const width = d.x1 - d.x0
        const height = d.y1 - d.y0
        if (width < 65 || height < 35) return ''
        return d.data.name
      })
      .each(function(d: TreemapNode) {
        const self = d3.select(this)
        const width = d.x1 - d.x0
        const text = self.text()
        if (text.length * 6.5 > width - 12) {
          self.text(text.substring(0, Math.floor(width / 6.5) - 3) + '...')
        }
      })

    // Add title tooltips
    cell.append('title')
      .text((d: TreemapNode) => {
        const occ = d.data.data
        return `${occ.title}\n` +
               `Category: ${getCategory(occ.anzsco_code)}\n` +
               `Employment: ${(occ.employment || 0).toLocaleString()}\n` +
               `AI Exposure: ${((occ.ai_exposure || 0) * 100).toFixed(0)}%\n` +
               `Median Pay: $${(occ.median_pay_aud || 0).toLocaleString()}`
      })

  }, [occupations, router, sortBy])

  return (
    <div className="card-brutal p-3 sm:p-4" role="region" aria-label="Interactive treemap of Australian occupations">
      {/* Header - stacked on mobile */}
      <div className="mb-3 sm:mb-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-4">
        <h2 className="text-lg sm:text-xl font-bold text-black">
          AUSTRALIAN OCCUPATIONS
        </h2>
        
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4">
          {/* Sort controls */}
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <label htmlFor="treemap-sort" className="text-xs sm:text-sm font-bold text-black whitespace-nowrap">Group by:</label>
            <select
              id="treemap-sort"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as SortOption)}
              className="select-brutal text-xs sm:text-sm flex-1 sm:flex-none"
              aria-describedby="sort-description"
            >
              <option value="employment">Workforce Size</option>
              <option value="disruption">Disruption Impact</option>
              <option value="ai_exposure">AI Exposure</option>
              <option value="category">Job Category</option>
            </select>
            <span id="sort-description" className="sr-only">Changes how occupations are grouped in the visualization</span>
          </div>
          
          {/* Legend - brutal badges */}
          <div className="flex items-center gap-1.5 sm:gap-2" role="img" aria-label="Color legend: Green means low AI impact, Yellow means medium impact, Red means high AI impact">
            <span className="badge-success text-[10px] sm:text-xs px-2 sm:px-3">Low</span>
            <span className="badge-warning text-[10px] sm:text-xs px-2 sm:px-3">Med</span>
            <span className="badge-danger text-[10px] sm:text-xs px-2 sm:px-3">High</span>
          </div>
        </div>
      </div>
      
      {/* SVG container with brutal border */}
      <div className="border-2 border-black rounded-[5px] overflow-hidden overflow-x-auto">
        <svg ref={svgRef} className="min-w-[600px] sm:min-w-0" role="img" aria-label={`Treemap showing ${occupations.length} Australian occupations grouped by ${sortBy === 'employment' ? 'workforce size' : sortBy === 'disruption' ? 'disruption impact' : sortBy === 'ai_exposure' ? 'AI exposure level' : 'job category'}. Each box represents an occupation - larger boxes mean ${sortBy === 'disruption' ? 'more workers affected by AI' : 'more workers'}, color indicates AI exposure risk. Click any box for details.`}></svg>
      </div>
      
      <p className="mt-2 sm:mt-3 text-xs sm:text-sm font-medium text-black" id="treemap-help">
        <span className="hidden sm:inline">Box size = workforce size • Color = AI exposure • Click any occupation for task breakdown</span>
        <span className="sm:hidden">Tap any box for details</span>
      </p>
    </div>
  )
}
