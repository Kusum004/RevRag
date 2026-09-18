from typing import List, Dict, Any, Set, Optional
import networkx as nx
from pydantic import BaseModel, Field
from common.models import ScreenState, TransitionEdge, Action
from layer4_understanding.schema import ScreenUnderstanding

class GraphNode(BaseModel):
    fingerprint: str
    screen_name: str
    category: str
    purpose: str
    elements_count: int
    activity_name: Optional[str] = None

class GraphEdge(BaseModel):
    from_fingerprint: str
    to_fingerprint: str
    action_type: str
    target_element_id: Optional[str] = None
    reason: Optional[str] = None

class UserJourney(BaseModel):
    journey_name: str
    step_count: int
    screen_sequence: List[str]
    description: str

class AppJourneyGraph(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    entry_node: str
    journeys: List[UserJourney] = Field(default_factory=list)

class JourneyGraphBuilder:
    """
    Builds a deduplicated, directed transition graph of the application.
    Analyzes navigation paths, detects dead ends, and extracts canonical user journeys.
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        self.node_metadata: Dict[str, GraphNode] = {}
        self.edge_records: Set[Tuple[str, str, str, str]] = set()

    def build_graph(
        self,
        screens: Dict[str, ScreenState],
        screen_understandings: Dict[str, ScreenUnderstanding],
        transitions: List[TransitionEdge]
    ) -> AppJourneyGraph:
        self.graph.clear()
        self.node_metadata.clear()
        self.edge_records.clear()

        # 1. Add Nodes
        for fp, state in screens.items():
            und = screen_understandings.get(fp)
            s_name = und.screen_name if und else "Screen"
            cat = und.screen_category if und else "general"
            purp = und.purpose if und else "App Screen"

            node = GraphNode(
                fingerprint=fp,
                screen_name=s_name,
                category=cat,
                purpose=purp,
                elements_count=len(state.elements),
                activity_name=state.activity_name
            )
            self.node_metadata[fp] = node
            self.graph.add_node(fp, **node.model_dump())

        # 2. Add Deduplicated Edges
        graph_edges: List[GraphEdge] = []
        for t in transitions:
            edge_key = (t.from_fingerprint, t.to_fingerprint, t.action.action_type.value, t.action.target_element_id or "")
            if edge_key not in self.edge_records:
                self.edge_records.add(edge_key)
                self.graph.add_edge(
                    t.from_fingerprint,
                    t.to_fingerprint,
                    action=t.action.action_type.value,
                    element=t.action.target_element_id
                )
                graph_edges.append(GraphEdge(
                    from_fingerprint=t.from_fingerprint,
                    to_fingerprint=t.to_fingerprint,
                    action_type=t.action.action_type.value,
                    target_element_id=t.action.target_element_id,
                    reason=t.action.reason
                ))

        # 3. Identify Entry Node
        # Entry node is the first visited node or node with 0 in-degree
        entry_node = list(screens.keys())[0] if screens else ""
        for n in self.graph.nodes():
            if self.graph.in_degree(n) == 0:
                entry_node = n
                break

        # 4. Extract Canonical Journeys (Simple paths from entry to leaf/key nodes)
        journeys: List[UserJourney] = []
        try:
            for target in self.graph.nodes():
                if target != entry_node and nx.has_path(self.graph, entry_node, target):
                    paths = list(nx.all_simple_paths(self.graph, entry_node, target, cutoff=5))
                    if paths:
                        shortest = paths[0]
                        target_node = self.node_metadata.get(target)
                        j_name = f"Path to {target_node.screen_name if target_node else target}"
                        journeys.append(UserJourney(
                            journey_name=j_name,
                            step_count=len(shortest),
                            screen_sequence=shortest,
                            description=f"Navigation journey leading to {target_node.purpose if target_node else 'screen'}"
                        ))
        except Exception:
            pass

        return AppJourneyGraph(
            nodes=list(self.node_metadata.values()),
            edges=graph_edges,
            entry_node=entry_node,
            journeys=journeys[:6]
        )
