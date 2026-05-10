import { GraphData } from "../types/graph"

export function buildGraph(domains: any[]): GraphData {
  const nodes: any[] = []
  const links: any[] = []
  const appSet = new Set()

  domains.forEach((domain, i) => {
    const domainId = `domain-${i}`

    nodes.push({ id: domainId, type: "domain" })

    domain.forEach((app: any) => {
      const appId = `${app.namespace}-${app.id}`

      if (!appSet.has(appId)) {
        nodes.push({ id: appId, type: "application" })
        appSet.add(appId)
      }

      links.push({
        source: domainId,
        target: appId
      })
    })
  })

  return { nodes, links }
}