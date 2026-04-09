
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from Group_13_Spec_day5VinAi.src.tools import check_date_of_next_appointment, book_appointment, cancel_appointment, get_diagnosis, PATIENT_DATA
from dotenv import load_dotenv

load_dotenv()

with open("system_prompt.txt", "r", encoding = "utf-8") as f:
    SYSTEM_PROMPT = f.read()

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

tools = [check_date_of_next_appointment, book_appointment, cancel_appointment, get_diagnosis]
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
llm_with_tools = llm.bind_tools(tools)


def agent_node(state: AgentState):

    messages = state["messages"]

    if not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    response = llm_with_tools.invoke(messages)
    #LOGGING lưu vào file log.txt
    with open("log.txt", "a", encoding="utf-8") as log_file:
        log_file.write("User: " + str(messages[-1].content) + "\n")
        log_file.write("Agent: " + str(response.content) + "\n")
        if response.tool_calls:
            for tc in response.tool_calls:
                log_file.write(f"Gọi tool: {tc['name']}({tc['args']})\n")
        else:
            log_file.write("Trả lời trực tiếp\n")
        log_file.write("-" * 40 + "\n")
    if response.tool_calls:
        for tc in response.tool_calls:
            print(f"Gọi tool: {tc['name']}({tc['args']})")
    else:
        print("Trả lời trực tiếp")

    return {"messages": [response]}

builder = StateGraph(AgentState)

builder.add_node("agent", agent_node)

tool_node = ToolNode(tools)

builder.add_node("tools", tool_node)

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")
builder.add_edge("agent", END)

graph = builder.compile()

if __name__ == "__main__":
    print("=" * 60)
    print("VinMec Assistant - Trợ lý ảo chăm sóc sức khỏe của bạn")
    print("Gõ 'quit' để thoát.")
    print("=" * 60)

    while True:
        user_input = input("Bạn: ").strip()
        if user_input.lower() == "quit":
            print("Cảm ơn bạn đã sử dụng VinMec Assistant. Chúc bạn thật nhiều sức khỏe!")
            break
        print("VinMec Assistant đang suy nghĩ...")
        result = graph.invoke({"messages": [HumanMessage(content=user_input)]})
        final = result["messages"][-1]
        print("VinMec Assistant: " + final.content)