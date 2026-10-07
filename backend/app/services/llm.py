from typing import Any
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage
from app.config import settings
from app.utils.logger import logger


class LLMService:
    """Service class for interaction with Groq LLM model."""

    def __init__(self) -> None:
        """Initialize the ChatGroq model using configured environment variables."""
        logger.info("Initializing Groq LLM Service...")
        if not settings.GROQ_API_KEY:
            logger.error("Failed to initialize LLMService: GROQ_API_KEY is not configured.")
            raise ValueError("GROQ_API_KEY must be provided in settings.")
        
        try:
            self._llm = ChatGroq(
                api_key=settings.GROQ_API_KEY,
                model=settings.GROQ_MODEL,
                temperature=0,
            )
            logger.info(f"Groq LLM Service initialized with model: {settings.GROQ_MODEL}")
        except Exception as e:
            logger.error(f"Error during ChatGroq model initialization: {e}", exc_info=True)
            raise e

    def invoke(self, prompt: str, **kwargs: Any) -> BaseMessage:
        """Invoke the LLM with the provided prompt text.
        
        Args:
            prompt (str): The prompt message to be sent.
            **kwargs: Extra parameters to pass to the LangChain invoke method.
            
        Returns:
            BaseMessage: The message returned from the ChatGroq model.
            
        Raises:
            Exception: If invocation fails.
        """
        logger.debug(f"Invoking LLM with prompt: '{prompt[:50]}...'")
        try:
            return self._llm.invoke(prompt, **kwargs)
        except Exception as e:
            logger.error(f"Failed to invoke LLM: {e}", exc_info=True)
            raise e

    def with_structured_output(self, schema: Any, **kwargs: Any) -> Any:
        """Expose LangChain's structured output capability.

        Args:
            schema: The Pydantic model class or Dict schema to structure output.
            **kwargs: Extra parameters to pass to with_structured_output.

        Returns:
            A runnable sequence that returns the structured output.
        """
        logger.debug(f"Creating structured output runnable for schema: {schema}")
        try:
            return self._llm.with_structured_output(schema, **kwargs)
        except Exception as e:
            logger.error(f"Failed to create structured output: {e}", exc_info=True)
            raise e


# Create the singleton LLM service instance
llm_service = LLMService()
