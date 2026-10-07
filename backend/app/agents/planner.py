from typing import Optional
from app.models.planner_models import PlannerOutput
from app.services.llm import llm_service
from app.prompts.planner_prompt import SYSTEM_PROMPT
from app.utils.logger import logger
from langchain_core.prompts import ChatPromptTemplate


class PlannerAgent:
    """Agent responsible for parsing the user's query and structuring the audit plan."""

    def __init__(self) -> None:
        """Initialize the PlannerAgent by binding the LLM with structured output."""
        logger.info("Initializing PlannerAgent with structured output...")
        try:
            self._structured_llm = llm_service.with_structured_output(PlannerOutput)
            self._prompt_template = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT),
                ("human", "{question}")
            ])
            self._chain = self._prompt_template | self._structured_llm
        except Exception as e:
            logger.error(f"Failed to initialize PlannerAgent chain: {e}", exc_info=True)
            raise e

    def plan(self, question: str) -> PlannerOutput:
        """Execute the planning chain on the input question to produce structured output.

        Args:
            question (str): The user's compliance question.

        Returns:
            PlannerOutput: Validated planner fields.
        """
        logger.info(f"PlannerAgent executing for question: '{question[:60]}...'")
        try:
            result: PlannerOutput = self._chain.invoke({"question": question})
            logger.info(f"PlannerAgent completed execution. Result: {result}")
            return result
        except Exception as e:
            logger.error(f"PlannerAgent invocation failed: {e}", exc_info=True)
            raise ValueError(f"Failed to parse planner output from LLM: {e}")
