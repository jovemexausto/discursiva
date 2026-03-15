import pytest

from discursiva_domain.entities import SubmissionStatus
from discursiva_domain.services import compute_score
from discursiva_domain.use_cases import (
    CorrectSubmission,
    GetSubmission,
    GetSubmissionQuery,
    ListSubmissions,
    ListSubmissionsQuery,
    SubmissionNotFound,
    SubmitAnswer,
    SubmitAnswerCommand,
)
from discursiva_domain.value_objects import Score
from .fakes import FakeQueue, FakeStorage, FakeSubmissionRepository



@pytest.fixture
def repo() -> FakeSubmissionRepository:
    return FakeSubmissionRepository()

@pytest.fixture
def storage() -> FakeStorage:
    return FakeStorage()

@pytest.fixture
def queue() -> FakeQueue:
    return FakeQueue()



def test_score_valid():
    assert Score(7.5).value == 7.5

def test_score_boundaries():
    assert Score(0.0).value == 0.0
    assert Score(10.0).value == 10.0

def test_score_invalid():
    with pytest.raises(ValueError):
        Score(10.1)
    with pytest.raises(ValueError):
        Score(-0.1)



def test_corrector_empty():
    assert compute_score("").value == 0.0

def test_corrector_short_text_low_score():
    assert compute_score("Olá mundo.").value < 5.0

def test_corrector_rich_text_high_score():
    text = (
        "A educação brasileira enfrenta desafios significativos no século XXI.\n"
        "Entre os principais problemas, destaca-se a desigualdade de acesso ao "
        "ensino de qualidade nas diferentes regiões do país.\n"
        "Investimentos em infraestrutura, capacitação de professores e tecnologia "
        "são fundamentais para superar essas dificuldades estruturais."
    )
    assert compute_score(text).value >= 7.0

def test_corrector_max_10():
    text = " ".join(["extraordinário"] * 20 + ["maravilhoso"] * 20 + ["fantástico"] * 20)
    assert compute_score(text).value <= 10.0



async def test_submit_answer_creates_pending_submission(repo, storage, queue):
    use_case = SubmitAnswer(repo=repo, storage=storage, queue=queue)
    submission = await use_case.execute(SubmitAnswerCommand(student_id="s1", text="texto"))

    assert submission.status == SubmissionStatus.PENDING
    assert submission.student_id == "s1"
    assert submission.score is None
    assert len(queue.published) == 1
    assert queue.published[0]["submission_id"] == str(submission.id)


async def test_submit_answer_uploads_to_storage(repo, storage, queue):
    use_case = SubmitAnswer(repo=repo, storage=storage, queue=queue)
    submission = await use_case.execute(SubmitAnswerCommand(student_id="s1", text="meu texto"))

    text = await storage.download(submission.s3_key)
    assert text == "meu texto"


async def test_get_submission_found(repo, storage, queue):
    sub = await SubmitAnswer(repo, storage, queue).execute(
        SubmitAnswerCommand(student_id="s1", text="t")
    )
    result = await GetSubmission(repo).execute(GetSubmissionQuery(str(sub.id)))
    assert result.id == sub.id

async def test_get_submission_not_found(repo):
    import uuid
    with pytest.raises(SubmissionNotFound):
        await GetSubmission(repo).execute(GetSubmissionQuery(str(uuid.uuid4())))

async def test_get_submission_invalid_id(repo):
    with pytest.raises(SubmissionNotFound):
        await GetSubmission(repo).execute(GetSubmissionQuery("not-a-uuid"))


async def test_list_submissions_pagination(repo, storage, queue):
    uc = SubmitAnswer(repo, storage, queue)
    for i in range(5):
        await uc.execute(SubmitAnswerCommand(student_id="s2", text=f"texto {i}"))

    page = await ListSubmissions(repo).execute(
        ListSubmissionsQuery(student_id="s2", limit=2, offset=0)
    )
    assert page.total == 5
    assert len(page.items) == 2

async def test_list_submissions_empty(repo):
    page = await ListSubmissions(repo).execute(
        ListSubmissionsQuery(student_id="ninguem")
    )
    assert page.total == 0
    assert page.items == []


async def test_correct_submission_marks_done(repo, storage, queue):
    text = (
        "A educação enfrenta desafios significativos.\n"
        "Investimentos são necessários para superar dificuldades.\n"
        "Tecnologia e infraestrutura são fundamentais para o desenvolvimento."
    )
    sub = await SubmitAnswer(repo, storage, queue).execute(
        SubmitAnswerCommand(student_id="s3", text=text)
    )

    messages = await queue.receive()
    await CorrectSubmission(repo, storage, queue).execute(messages[0])

    corrected = await repo.get(sub.id)
    assert corrected.status == SubmissionStatus.DONE
    assert corrected.score is not None
    assert corrected.score.value >= 5.0


async def test_correct_submission_idempotent(repo, storage, queue):
    """Mensagem duplicada não deve reprocessar uma submission já DONE."""
    text = "Texto de teste com palavras suficientes para obter nota."
    sub = await SubmitAnswer(repo, storage, queue).execute(
        SubmitAnswerCommand(student_id="s4", text=text)
    )

    messages = await queue.receive()
    msg = messages[0]

    # Processa uma vez
    await CorrectSubmission(repo, storage, queue).execute(msg)

    # Simula redelivery,  reinsere a mesma mensagem na fila
    from discursiva_domain.ports import CorrectionMessage
    dup = CorrectionMessage(
        submission_id=str(sub.id),
        s3_key=sub.s3_key,
        receipt_handle="receipt-dup",
    )
    await CorrectSubmission(repo, storage, queue).execute(dup)

    corrected = await repo.get(sub.id)
    assert corrected.status == SubmissionStatus.DONE  # não voltou para PROCESSING
