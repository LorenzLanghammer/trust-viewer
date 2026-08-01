import * as d3 from "d3"
import { useEffect, useRef } from "react"
import { ApplicationState, GroupState } from "../types/graph"

export function Graph({
  domains,
  groups,
  applications,
  onNodeClick,
  onGroupClick,
  showDomainHulls,
  showGroupHulls
}: {
  domains: (number | string)[][]
  groups: GroupState[]
  applications: Record<number, string>
  onNodeClick: (id: string) => void
  onGroupClick: (groupIndex: number) => void
  showDomainHulls: boolean
  showGroupHulls: boolean

}) {

  const ref = useRef<SVGSVGElement | null>(null)
  const width = window.innerWidth
  const height = window.innerHeight

  useEffect(() => {
    if (!ref.current) return;

    const svg = d3.select(ref.current);

    svg
      .selectAll(".domain-hull")
      .style("display", showDomainHulls ? null : "none" as any);

    svg
      .selectAll(".group-hull")
      .style("display", showGroupHulls ? null : "none" as any);

  }, [showDomainHulls, showGroupHulls]);

  useEffect(() => {
    if (!ref.current) return

    const allIdsSet = new Set<string>()

    domains.flat().forEach(m => {
      if (m !== undefined && m !== null) allIdsSet.add(String(m))
    })

    ;(groups || []).forEach(group => {
      ;(group.applicationIds || []).forEach(appId => {
        if (appId !== undefined && appId !== null) {
          allIdsSet.add(String(appId))
        }
      })
    })


    const allIds = Array.from(allIdsSet)
    console.log("applications")
    console.log(applications)

    const domainNodes = domains.map((_, idx) => ({
      id: `domain-${idx}`,
      type: "domain"
    }))

    const groupNodes = (groups || []).map((arr, idx) => ({
      id: arr.groupId,
      type: "group",
      idx
    }))

    const memberNodes = allIds.map(id => ({
      id,
      type: "member",
      name: applications[id] || "Unnamed",
      radius: 18
    }))

    console.log("member nodes")
    console.log(memberNodes)

    const nodes = [...domainNodes, ...groupNodes, ...memberNodes]

    const domainLinks = domains.flatMap((arr, idx) =>
      arr
        .filter(m => m !== undefined && m !== null)
        .map(m => ({
          source: `domain-${idx}`,
          target: String(m)
        }))
    )

    const groupLinks = (groups || []).flatMap((arr, idx) =>
      arr['applicationIds']
        .filter(g => g !== undefined && g !== null)
        .map(g => ({
          source: arr.groupId,
          target: String(g)
        }))
    )

    const links = [...domainLinks, ...groupLinks]

    const svg = d3.select(ref.current)
    svg.selectAll("*").remove()

    const centerX = width / 2
    const centerY = height / 2
    const radius = Math.min(width, height) / 4
    const groupRadius = radius * 0.6

    const domainTargets = new Map<string, { x: number; y: number }>()
    domainNodes.forEach((d, i) => {
      const a = (i / Math.max(1, domainNodes.length)) * Math.PI * 2
      domainTargets.set(d.id, {
        x: centerX + radius * Math.cos(a),
        y: centerY + radius * Math.sin(a)
      })
    })

    const groupTargets = new Map<string, { x: number; y: number }>()
    groupNodes.forEach((g, i) => {
      const a = (i / Math.max(1, groupNodes.length)) * Math.PI * 2
      groupTargets.set(String(g.id), {
        x: centerX + groupRadius * Math.cos(a),
        y: centerY + groupRadius * Math.sin(a)
      })
    })

    const getGroupIndexForNode = (nodeId: string): number | null => {
      const appId = Number(nodeId)
      const idx = groups.findIndex((g) => g.applicationIds.includes(appId))
      return idx >= 0 ? idx : null
    }

    const getMemberTarget = (node: any) => {
      if (node.type !== "member") {
        return { x: centerX, y: centerY }
      }

      const groupIndex = getGroupIndexForNode(node.id)
      if (groupIndex === null) {
        return { x: centerX, y: centerY }
      }

      const groupNode = groupNodes[groupIndex]
      return (
        groupTargets.get(String(groupNode.id)) ?? { x: centerX, y: centerY }
      )
    }

    const members = nodes.filter((n: any) => n.type === "member")
    const groupAnchors = nodes.filter((n: any) => n.type === "group")

    const simulation = d3
      .forceSimulation(nodes as any)
      .force(
        "link",
        d3
          .forceLink(links as any)
          .id((d: any) => d.id)
          .distance(120)
          .strength(0.05)
      )
      .force(
        "charge",
        d3.forceManyBody().strength((d: any) =>
          d.type === "domain" ? -800 : d.type === "group" ? -500 : -200
        )
      )
      .force("center", d3.forceCenter(centerX, centerY))
      .force("x", d3.forceX().x((d: any) => {
        if (d.type === "domain") return domainTargets.get(d.id)?.x ?? centerX
        if (d.type === "group") return groupTargets.get(String(d.id))?.x ?? centerX
        return getMemberTarget(d).x
      }).strength((d: any) => (d.type === "member" ? 0.12 : 0.05)))

      .force("y", d3.forceY().y((d: any) => {
        if (d.type === "domain") return domainTargets.get(d.id)?.y ?? centerY
        if (d.type === "group") return groupTargets.get(String(d.id))?.y ?? centerY
        return getMemberTarget(d).y
      }).strength((d: any) => (d.type === "member" ? 0.12 : 0.05)))
      .force(
        "collide",
        d3.forceCollide().radius((d: any) =>
          d.radius ?? 18
        ).strength(1)
      ).
      force("bounds", () => {
          const padding = 40

          nodes.forEach((node: any) => {
            const r = node.radius ?? 18
            const minX = padding + r
            const maxX = width - padding - r
            const minY = padding + r
            const maxY = height - padding - r

            if (node.x < minX) {
              node.x = minX
              node.vx = Math.max(node.vx, 0)
            } else if (node.x > maxX) {
              node.x = maxX
              node.vx = Math.min(node.vx, 0)
            }

            if (node.y < minY) {
              node.y = minY
              node.vy = Math.max(node.vy, 0)
            } else if (node.y > maxY) {
              node.y = maxY
              node.vy = Math.min(node.vy, 0)
            }
          })
        }).
        force("groupSeparation", forceGroupSeparation(getGroupIndexForNode, 180, 0.9))

    const nodeMap = new Map<string, any>()
    simulation.nodes().forEach((n: any) => nodeMap.set(String(n.id), n))
    
    const findGroupForNode = (nodeId: string): number | null => {
      for (let i = 0; i < groups.length; i++) {
        if (groups[i].applicationIds.includes(Number(nodeId))) {
          return i;
        }
      }
      return null;
    };

    const lineGen = d3
      .line<[number, number]>()
      .curve(d3.curveCardinalClosed.tension(0.85))

    const domainHullGroup = svg.append("g")

   const domainHullPath = domainHullGroup
      .selectAll("path")
      .data(domainNodes)
      .enter()
      .append("path")
      .style("display", showDomainHulls ? "inline" : "none")
      .attr("fill", "rgba(255,0,0,0.06)")
      .attr("stroke", "red")
      .attr("stroke-width", 1.5)
      .attr("class", "domain-hull")

    const groupHullGroup = svg.append("g")

    const groupHullPath = groupHullGroup
      .selectAll("path")
      .data(groupNodes)
      .enter()
      .append("path")
      .style("display", showGroupHulls ? "inline" : "none")      .attr("fill", "rgba(0,128,0,0.08)")
      .attr("stroke", "green")
      .attr("stroke-width", 1.2)
      .attr("class", "group-hull")
      .on("click", (_event, d: any) => {
        onGroupClick(d.id)
      })

    const node = svg
      .append("g")
      .selectAll("g")
      .data(memberNodes)
      .enter()
      .append("g")

    const labels = svg
      .append("g")
      .selectAll("text")
      .data(memberNodes)
      .enter()
      .append("text")
      .text((d: any) => d.name)
      .attr("font-size", 10)
      .attr("text-anchor", "middle")
      .attr("fill", "black")
      .attr("pointer-events", "none")
    
    const circles = node
      .insert("circle", "text")
      .attr("fill", "rgba(120,120,120,0.3)")
      .attr("stroke", "rgba(80,80,80,0.8)")
      .attr("stroke-width", 1)
      .attr("r", function (_d: any, i: number) {
        const textNode = labels.nodes()[i]
        const bbox = textNode.getBBox()

        return Math.max(bbox.width / 2 + 14, 18)
      })

    circles.attr("r", function(d: any, i) {
      const bbox = labels.nodes()[i].getBBox();
      d.radius = Math.max(bbox.width / 2 + 14, 18);
      return d.radius;
    });
      

    const drag = d3.drag<SVGRectElement, any>()
      .on("start", (event, d) => {
        d.fx = d.x;
        d.fy = d.y;
      })
      .on("drag", (event, d) => {
        d.fx = event.x;
        d.fy = event.y;

        d.x = event.x;
        d.y = event.y;

        updateGraph();
      })
      .on("end", (event, d) => {
        d.fx = event.x;
        d.fy = event.y;

        d.x = event.x;
        d.y = event.y;

        updateGraph();
      })
      .on("end", (event, d) => {
        d.fx = event.x;
        d.fy = event.y;
      })
      
      node.call(drag as any)
      node.on("click", (event, d: any) => {
        if (d.type === "member") {
          onNodeClick(d.id)
        }
      })
    
    function forceGroupSeparation(
      getGroupIndexForNode: (id: string) => number | null,
      minDistance: number,
      strength: number
    ) {
      let nodes: any[] = []

      function force(alpha: number) {
        const members = nodes.filter((n: any) => n.type === "member")

        for (let i = 0; i < members.length; i++) {
          const a = members[i]
          const gA = getGroupIndexForNode(a.id)
          if (gA === null) continue

          for (let j = i + 1; j < members.length; j++) {
            const b = members[j]
            const gB = getGroupIndexForNode(b.id)
            if (gB === null || gB === gA) continue

            const dx = (b.x ?? 0) - (a.x ?? 0)
            const dy = (b.y ?? 0) - (a.y ?? 0)
            const dist = Math.sqrt(dx * dx + dy * dy) || 1

            if (dist < minDistance) {
              const push = ((minDistance - dist) / dist) * strength * alpha
              const fx = dx * push
              const fy = dy * push
              a.vx -= fx; a.vy -= fy
              b.vx += fx; b.vy += fy
            }
          }
        }
      }

      force.initialize = (ns: any[]) => { nodes = ns }
      return force
    }
    
    function updateGraph() {

      const buildHull = (points: [number, number][], padding: number, padding_two: number) => {
        if (points.length === 0) return ""

        if (points.length === 1) {
          const [x, y] = points[0]
          const r = padding
          return `
            M ${x - r},${y}
            a ${r},${r} 0 1,0 ${r * 2},0
            a ${r},${r} 0 1,0 ${-r * 2},0
          `
        }
        if (points.length === 2) {
          const [p0, p1] = points

          const dx = p1[0] - p0[0]
          const dy = p1[1] - p0[1]
          const len = Math.hypot(dx, dy) || 1

          // unit vector along the line
          const ux = dx / len
          const uy = dy / len

          // unit vector perpendicular to the line
          const px = -uy
          const py = ux

          const r = padding_two * 1.5

          const A = [p0[0] - ux * padding_two, p0[1] - uy * padding_two]
          const B = [p1[0] + ux * padding_two, p1[1] + uy * padding_two]

          const A1: [number, number] = [A[0] + px * r, A[1] + py * r]
          const B1: [number, number] = [B[0] + px * r, B[1] + py * r]
          const B2: [number, number] = [B[0] - px * r, B[1] - py * r]
          const A2: [number, number] = [A[0] - px * r, A[1] - py * r]

          return lineGen([A1, B1, B2, A2]) || ""
        }

        const hull = d3.polygonHull(points)
        if (!hull) return ""

        const c = d3.polygonCentroid(hull)

        const expanded = hull.map(p => {
          const dx = p[0] - c[0]
          const dy = p[1] - c[1]
          const len = Math.hypot(dx, dy) || 1

          const expansion = len + padding + 30

          return [
            c[0] + (dx / len) * expansion,
            c[1] + (dy / len) * expansion
          ] as [number, number]
        })

        return lineGen(expanded) || ""
      }

      domainHullPath.attr("d", (_d, i) => {
        const pts: [number, number][] = []

        ;(domains[i] || []).forEach(m => {
          const n = nodeMap.get(String(m))
          if (
            n &&
            typeof n.x === "number" &&
            typeof n.y === "number"
          ) {
            pts.push([n.x, n.y])
          }
        })

        return buildHull(pts, 50, 20)
      })

      groupHullPath.attr("d", (_d, i) => {
        const pts: [number, number][] = []

        ;(groups?.[i]?.applicationIds || []).forEach(g => {
          const n = nodeMap.get(String(g))
          if (
            n &&
            typeof n.x === "number" &&
            typeof n.y === "number"
          ) {
            pts.push([n.x, n.y])
          }
        })

        return buildHull(pts, 70, 30)
      })

      node.attr(
        "transform",
        (d: any) => `translate(${d.x},${d.y})`
      )
      labels
      .attr("x", (d: any) => d.x)
      .attr("y", (d: any) => d.y + 4)
    }

    //simulation.on("tick", updateGraph)
    for (let i = 0; i < 300; i++) {
      simulation.tick();
    }

    simulation.stop();

    updateGraph();
    return () => simulation.stop()
  }, [domains, groups])


  return <svg ref={ref} width={width} height={height} />
}