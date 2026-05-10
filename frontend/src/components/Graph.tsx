import * as d3 from "d3"
import { useEffect, useRef } from "react"

export function Graph({ domains, groups }: { domains: (number | string)[][], groups?: Array<Array<{namespace: number | null, id: number | string}>> }) {
  const ref = useRef<SVGSVGElement | null>(null)
  const width = window.innerWidth
  const height = window.innerHeight

  useEffect(() => {
    if (groups) console.log('certificate groups', groups)
    if (!ref.current) return

    // Normalize member ids to strings so domain and group memberships match
    const allIdsSet = new Set<string>()
    domains.flat().forEach((m: any) => { if (m !== undefined && m !== null) allIdsSet.add(String(m)) })
    if (groups) {
      groups.flat().forEach((g: any) => { if (g && g.id !== undefined && g.id !== null) allIdsSet.add(String(g.id)) })
    }

    const allIds = Array.from(allIdsSet)

    const domainNodes = domains.map((_, idx) => ({ id: `domain-${idx}`, type: 'domain' }))
    const groupNodes = (groups || []).map((_, idx) => ({ id: `group-${idx}`, type: 'group' }))
    const memberNodes = allIds.map(id => ({ id, type: 'member' }))
    const nodes = [...domainNodes, ...groupNodes, ...memberNodes]

    const domainLinks = domains.flatMap((domainArr, idx) => {
      const centerId = `domain-${idx}`
      return domainArr
        .filter((m: any) => m !== undefined && m !== null)
        .map((member: any) => ({ source: centerId as string, target: String(member) }))
    })

    const groupLinks = (groups || []).flatMap((groupArr, idx) => {
      const centerId = `group-${idx}`
      return groupArr
        .filter((g: any) => g && g.id !== undefined && g.id !== null)
        .map((member: any) => ({ source: centerId as string, target: String(member.id) }))
    })

    const links = [...domainLinks, ...groupLinks]


    const svg = d3.select(ref.current)
    svg.selectAll("*").remove()

    const centerX = width / 2
    const centerY = height / 2
    const radius = Math.min(width, height) / 4
    const groupRadius = radius * 0.6
    const domainTargets = new Map<string, { x: number; y: number }>()
    domainNodes.forEach((dn: any, idx: number) => {
      const angle = (idx / Math.max(1, domainNodes.length)) * Math.PI * 2
      domainTargets.set(dn.id, { x: centerX + radius * Math.cos(angle), y: centerY + radius * Math.sin(angle) })
    })
    const groupTargets = new Map<string, { x: number; y: number }>()
    groupNodes.forEach((gn: any, idx: number) => {
      const angle = (idx / Math.max(1, groupNodes.length)) * Math.PI * 2
      groupTargets.set(gn.id, { x: centerX + groupRadius * Math.cos(angle), y: centerY + groupRadius * Math.sin(angle) })

    })

    const simulation = d3.forceSimulation(nodes as any)
      .force("link", d3.forceLink(links as any).id((d: any) => d.id).distance((d: any) => ((d.source.type === 'domain' || d.target.type === 'domain' || d.source.type === 'group' || d.target.type === 'group') ? 140 : 100)).strength(0.6))
      .force("charge", d3.forceManyBody().strength((d: any) => d.type === 'domain' ? -800 : d.type === 'group' ? -500 : -200).distanceMax(1000))
      .force("center", d3.forceCenter(centerX, centerY))
      .force("x", d3.forceX().x((d: any) => {
        if (d.type === 'domain') return domainTargets.get(d.id)?.x ?? centerX
        if (d.type === 'group') return groupTargets.get(d.id)?.x ?? centerX
        return centerX
      }).strength(0.06))
      .force("y", d3.forceY().y((d: any) => {
        if (d.type === 'domain') return domainTargets.get(d.id)?.y ?? centerY
        if (d.type === 'group') return groupTargets.get(d.id)?.y ?? centerY
        return centerY
      }).strength(0.06))
      .force("collide", d3.forceCollide().radius((d: any) => d.type === 'domain' || d.type === 'group' ? 36 : 18).strength(1.5))

    const link = svg.append("g")
      .selectAll("line")
      .data(links)
      .enter()
      .append("line")
      .attr("stroke", "black")

    link.style("opacity", 0.8)

    const node = svg.append("g")
      .selectAll("circle")
      .data(nodes)
      .enter()
      .append("circle")
      .attr("r", (d: any) => d.type === 'domain' ? 12 : d.type === 'group' ? 12 : 6)
      .attr("fill", (d: any) => d.type === 'domain' ? 'red' : d.type === 'group' ? 'green' : 'blue')
      .call(
        d3.drag<SVGCircleElement, any>()
          .on("start", (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart()
            d.fx = d.x
            d.fy = d.y
          })
          .on("drag", (event, d) => {
            d.fx = event.x
            d.fy = event.y
          })
          .on("end", (event, d) => {
            if (!event.active) simulation.alphaTarget(0)
            d.fx = null
            d.fy = null
          })
      )

    simulation.on("tick", () => {
      link
        .attr("x1", (d: any) => (d.source as any).x)
        .attr("y1", (d: any) => (d.source as any).y)
        .attr("x2", (d: any) => (d.target as any).x)
        .attr("y2", (d: any) => (d.target as any).y)

      node
        .attr("cx", (d: any) => d.x)
        .attr("cy", (d: any) => d.y)
    })

    return () => {
      simulation.stop()
      svg.selectAll("*").remove()
    }
  }, [domains])

  return <svg ref={ref} width={width} height={height} />
}