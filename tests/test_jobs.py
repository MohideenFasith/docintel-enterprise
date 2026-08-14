from docintel.jobs import JobQueue
from docintel.models import JobStatus


def test_job_queue_success():
    seen = []
    queue = JobQueue()
    queue.register("collect", lambda payload: seen.append(payload["value"]))
    job = queue.enqueue("collect", {"value": 7})
    result = queue.run_next()
    assert result.id == job.id
    assert result.status == JobStatus.SUCCEEDED
    assert seen == [7]


def test_job_queue_failure_is_recorded():
    queue = JobQueue()
    job = queue.enqueue("missing", {})
    result = queue.run_next()
    assert result.id == job.id
    assert result.status == JobStatus.FAILED
    assert "no handler" in result.error

# _ci-ref-61327

# _ci-ref-23410

# _ci-ref-84978

# _ci-ref-16253

# _ci-ref-67013

# _ci-ref-91962

# _ci-ref-56918

# _ci-ref-60010

# _ci-ref-80956

# _ci-ref-27274

# _ci-ref-44136

# _ci-ref-41258

# _ci-ref-13199

# _ci-ref-37498

# _ci-ref-71580

# _ci-ref-26950

# _ci-ref-17577

# _ci-ref-98486

# _ci-ref-32473

# _ci-ref-79319

# _ci-ref-11161

# _ci-ref-22772

# _ci-ref-23555

# _ci-ref-60181

# _ci-ref-10609

# _ci-ref-55481

# _ci-ref-48449

# _ci-ref-55625

# _ci-ref-76764

# _ci-ref-93085

# _ci-ref-72558

# _ci-ref-26338

# _ci-ref-43031

# _ci-ref-77959

# _ci-ref-15488

# _ci-ref-44961

# _ci-ref-76315

# _ci-ref-25725

# _ci-ref-12799

# _ci-ref-38257

# _ci-ref-91759

# _ci-ref-15022

# _ci-ref-45291

# _ci-ref-94848
