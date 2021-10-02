from typing import Optional

from pydantic import BaseModel


class SubmissionContradictionError(BaseException):
    pass


class Submission(BaseModel):
    """Submission Model from the frontend"""
    sensitivity: str
    id: str
    uid: str
    acquaintance: Optional[bool] = False
    colleagues: Optional[bool] = False
    family: Optional[bool] = False
    friends: Optional[bool] = False
    everybody: Optional[bool] = False
    nobody: Optional[bool] = False

    def check(self) -> list:
        """validates the model for contradictions"""
        demography = [self.acquaintance, self.colleagues,
                      self.family, self.friends, self.everybody,
                      self.nobody]
        if all(demography):
            raise SubmissionContradictionError("Contradiction: Everything is selected!")
        if all([not b for b in demography]):
            raise SubmissionContradictionError("Contradiction: Nothing is selected!")
        if self.nobody and self.everybody:
            raise SubmissionContradictionError("Contradiction: Everybody is not Nobody!")
        if self.nobody and any(demography[:-2]):
            raise SubmissionContradictionError("Contradiction: Nobody and another target demography were selected")

        return demography
