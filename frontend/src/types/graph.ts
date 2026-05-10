export interface Node {
  id: number
}

export interface GraphLink {
  source: number
  target: number
}

export interface GraphData {
  nodes: Node[]
  links: GraphLink[]
}

export interface Domains {
  domains: any[][]
}

export type GraphProps = {
  nodes: Node[];
  links: GraphLink[];
};
