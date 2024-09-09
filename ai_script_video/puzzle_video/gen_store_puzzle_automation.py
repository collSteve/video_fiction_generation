from ai_script_video.puzzle_video.automation_nodes.puzzle_generation import PuzzleGenerationTask
from ai_script_video.puzzle_video.automation_nodes.unprocessed_puzzle_fetcher import UnprocessedPuzzleFetcher
from automation.automation_graph import AutomationGraph
from automation.nodes.if_node import AutomationIFNode
from automation.nodes.save_json_db import SaveJsonDBTask
from automation.nodes.terminus_node import TerminusNode


graph = AutomationGraph()

fetch_node = UnprocessedPuzzleFetcher(graph, "fetch")
puzzle_gen_node = PuzzleGenerationTask(graph, "puzzle_gen")
db_store_node = SaveJsonDBTask(graph, "db_store")

db_store_node.specify_input_list_type("List[PuzzleDBItem]")

if_node = AutomationIFNode(graph, "if_node", lambda x: len(x) > 0)
if_node.configure_input_output("unprocessed_puzzles", "if_output", "List[RawPuzzle]")

puzzle_gen_node.add_input("if_unprocessed_puzzles", "List[RawPuzzle]")

start_node = TerminusNode(graph, "start")
end_node = TerminusNode(graph, "end")

start_node.add_input("puzzle_db_path", "path")
start_node.add_input("puzzle_creation_system_prompt_path", "path")

end_node.add_output("puzzles", "List[RawPuzzle]")

graph.add_node(fetch_node)
graph.add_node(puzzle_gen_node)
graph.add_node(db_store_node)
graph.add_node(if_node)
graph.add_node(start_node)
graph.add_node(end_node)

graph.set_start_node("start")
graph.set_end_node("end")

graph.add_link("start", "puzzle_db_path", "fetch", "puzzle_db_path")

graph.add_link("fetch", "unprocessed_puzzles", "if_node", "unprocessed_puzzles")
graph.add_link_from_if_node("if_node", "if_output", "puzzle_gen", "if_unprocessed_puzzles", False) # no branch
graph.add_link_from_if_node("if_node", "if_output", "end", "puzzles", True) # yes branch

graph.add_link("start", "puzzle_creation_system_prompt_path", "puzzle_gen", "puzzle_creation_system_prompt_path")
graph.add_link("start", "puzzle_db_path", "puzzle_gen", "puzzle_db_path")

graph.add_link("puzzle_gen", "generated_puzzles", "db_store", "json_obj_list")
graph.add_link("start", "puzzle_db_path", "db_store", "db_path")

fetch_node.add_input("route_from_json_saver", "router")
fetch_node.set_input_value("route_from_json_saver", "directing") # making routing links SET on start

graph.add_link("db_store", "directing", "fetch", "route_from_json_saver")

graph.set_input_value("puzzle_db_path", "puzzle_db.json")
graph.set_input_value("puzzle_creation_system_prompt_path", "ai_script_video\puzzle_video\puzzle_generation_prompt")

graph.execute()