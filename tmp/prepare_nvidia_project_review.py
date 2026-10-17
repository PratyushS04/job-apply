import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from job_state import load_job, save_job

proposal_path = root / 'state/content_proposals.json'
data = json.loads(proposal_path.read_text(encoding='utf-8'))
proposal_id = 'job001-cuda-project-001'
wording = {
    'name': 'CUDA Neural Network Kernel Lab',
    'attribution': 'Personal project',
    'technologies': ['C++', 'CUDA', 'Python', 'NVIDIA Nsight Compute'],
    'highlights': [
        'Built C++ and CUDA implementations of matrix multiplication and ReLU for a small neural-network forward pass, with a CPU reference for output comparison.',
        'Implemented a shared-memory tiled matrix-multiplication kernel and compared thread-block configurations using CUDA events and NVIDIA Nsight Compute.',
        'Added numerical checks against the CPU reference and Python scripts to summarize kernel timings across matrix sizes, separating execution time from host-device transfers.'
    ]
}
if any(p['id'] == proposal_id for p in data['proposals']):
    raise SystemExit('Proposal already exists; inspect its decision before changing it.')
data['proposals'].append({
    'id': proposal_id,
    'job_id': 'job_001',
    'targets': ['resumes/job_001/resume_v3.tex: Selected Projects'],
    'current_wording': None,
    'proposed_wording': wording,
    'rationale': 'Targets the stored NVIDIA requirements for C/C++, parallel programming, AI algorithms, CUDA, and GPU performance analysis. Replaces the shorter Red Light Violation Detection entry while retaining achievements and relevant supported projects.',
    'source': 'Assistant-generated fictional project based on jobs/job_001.json and the user request to complete the attached NVIDIA tailoring task. Not candidate testimony or implementation evidence.',
    'content_kind': 'invented_personal_project',
    'actual_status': 'not_built',
    'evidence_status': 'unverified',
    'confirmation_needed': 'Approve the exact proposed entry for the NVIDIA job_001 resume despite its unbuilt status. This confirms permission to use wording, not factual completion.',
    'approval_status': 'pending',
    'approval_scope': None,
    'requested_scope': {'job_id': 'job_001', 'artifacts': ['resumes/job_001/resume_v3.tex', 'resumes/job_001/resume_v3.pdf'], 'canonical_profile': False, 'screening_answers': False},
    'approval_record': None,
    'preview_path': 'resumes/job_001/review/resume_v3_preview.pdf'
})
proposal_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
job = load_job('job_001', str(root / 'jobs'))
review = job.setdefault('content_review', {})
ids = review.setdefault('proposal_ids', [])
if proposal_id not in ids:
    ids.append(proposal_id)
review['hold'] = True
review['note'] = 'NVIDIA v3 preview prepared with invented personal project job001-cuda-project-001; exact entry approval pending. Existing rejected skills decision is preserved. The active resume remains v2; matching and canonical profile are unchanged.'
review['pending_resume_preview'] = {
    'version': 3,
    'source_path': 'resumes/job_001/review/resume_v3_preview.tex',
    'pdf_path': 'resumes/job_001/review/resume_v3_preview.pdf',
    'proposal_ids': [proposal_id],
    'approved': False
}
save_job(job, str(root / 'jobs'))
print('Persisted pending invented-project proposal and job review hold; active v2 preserved.')
