import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def get_investigator_token():
    res = client.post('/api/auth/demo-login/investigator')
    return res.json()['access_token']

def get_citizen_token():
    res = client.post('/api/auth/demo-login/citizen')
    return res.json()['access_token']

def test_health():
    res = client.get('/health')
    assert res.status_code == 200
    assert res.json() == {'status': 'healthy'}

def test_get_alerts_as_investigator():
    token = get_investigator_token()
    res = client.get('/api/alerts', headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 5
    assert data[0]['priority_tier'] == 'CRITICAL'

def test_get_alerts_citizen_forbidden():
    token = get_citizen_token()
    res = client.get('/api/alerts', headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 403

def test_get_alert_detail():
    token = get_investigator_token()
    res = client.get('/api/alerts/1', headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200
    data = res.json()
    assert data['case_code'].startswith('CASE-')
    assert len(data['signals']) >= 1
    assert data['project_detail'] is not None
    assert data['vendor_detail'] is not None
    assert 'timeline' in data
    assert len(data['timeline']) >= 2
    assert 'inspections' in data
    assert 'quality_records' in data
    assert 'maintenance' in data

def test_vendor_network():
    token = get_investigator_token()
    res = client.get('/api/vendors/1/network', headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200
    data = res.json()
    assert 'nodes' in data
    assert 'edges' in data
    assert len(data['nodes']) >= 2

def test_kpis():
    res = client.get('/api/analytics/kpis')
    assert res.status_code == 200
    data = res.json()
    assert data['tenders_analyzed'] >= 5
    assert data['critical_cases'] >= 2

def test_tender_categories():
    res = client.get('/api/tenders/categories')
    assert res.status_code == 200
    cats = res.json()
    assert isinstance(cats, list)
    assert len(cats) >= 2
    assert 'Civil Construction' in cats or 'Road Infrastructure' in cats

def test_leaderboard():
    res = client.get('/api/reviewers/leaderboard')
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 3
    assert data[0]['user_name'] == 'Rohan Verma'
    assert data[0]['reputation_score'] >= 90.0

def test_auth_demo_login_and_me():
    res = client.post('/api/auth/demo-login/investigator')
    assert res.status_code == 200
    data = res.json()
    assert 'access_token' in data
    assert data['user']['role'] == 'INVESTIGATOR'
    token = data['access_token']

    res_me = client.get('/api/auth/me', headers={'Authorization': f'Bearer {token}'})
    assert res_me.status_code == 200
    assert res_me.json()['role'] == 'INVESTIGATOR'

def test_tenders_and_projects():
    res_tenders = client.get('/api/tenders')
    assert res_tenders.status_code == 200
    tenders_data = res_tenders.json()
    items = tenders_data['items'] if isinstance(tenders_data, dict) else tenders_data
    assert len(items) >= 5

    res_tender1 = client.get('/api/tenders/1')
    assert res_tender1.status_code == 200
    assert res_tender1.json()['tender_id'] == 'T001' or res_tender1.json().get('tender_code') == 'T001'

    res_bids = client.get('/api/tenders/1/bids')
    assert res_bids.status_code == 200
    assert len(res_bids.json()) >= 1

    res_projects = client.get('/api/projects')
    assert res_projects.status_code == 200
    assert len(res_projects.json()) >= 5

def test_investigation_note_and_status_update():
    token = get_investigator_token()
    headers = {'Authorization': f'Bearer {token}'}

    # Add note
    res_note = client.post('/api/investigations/1/notes', json={
        'note_text': 'Automated test investigation note verification.'
    }, headers=headers)
    assert res_note.status_code == 200
    assert res_note.json()['note_text'] == 'Automated test investigation note verification.'

    # Update status
    res_status = client.post('/api/investigations/1/status', json={
        'status': 'EVIDENCE_GATHERING',
        'note': 'Transitioned to evidence gathering stage for testing.'
    }, headers=headers)
    assert res_status.status_code == 200
    assert res_status.json()['new_status'] == 'EVIDENCE_GATHERING'

def test_complaints_flow():
    token = get_citizen_token()
    headers = {'Authorization': f'Bearer {token}'}

    # Submit complaint with tender_id
    res_comp = client.post('/api/complaints', json={
        'tender_id': 'T001',
        'title': 'Test road pothole report by citizen',
        'description': 'Discovered large pothole near KM 6 marker during morning commute.',
        'category': 'ROAD_QUALITY',
        'rating': 1,
        'location': 'NH-21 KM 6',
        'media_url': 'https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=600'
    }, headers=headers)
    assert res_comp.status_code == 200
    new_comp = res_comp.json()
    assert new_comp['title'] == 'Test road pothole report by citizen'
    assert new_comp['status'] == 'SUBMITTED'

    # Check my-reviews
    res_my = client.get('/api/complaints/my-reviews', headers=headers)
    assert res_my.status_code == 200
    my_list = res_my.json()
    assert any(c['id'] == new_comp['id'] for c in my_list)

    # Verify complaint as investigator
    inv_token = get_investigator_token()
    inv_headers = {'Authorization': f'Bearer {inv_token}'}

    res_verify = client.post(f"/api/complaints/{new_comp['id']}/verify", json={
        'status': 'VERIFIED'
    }, headers=inv_headers)
    assert res_verify.status_code == 200
    assert res_verify.json()['status'] == 'VERIFIED'

def test_leaderboard_and_categories():
    res_cats = client.get('/api/tenders/categories')
    assert res_cats.status_code == 200
    cats = res_cats.json()
    assert isinstance(cats, list)
    assert len(cats) > 0

    res_lb = client.get('/api/reviewers/leaderboard')
    assert res_lb.status_code == 200
    lb = res_lb.json()
    assert isinstance(lb, list)
    assert len(lb) > 0
    assert 'reputation_score' in lb[0]

    token = get_citizen_token()
    res_me = client.get('/api/reviewers/me', headers={'Authorization': f'Bearer {token}'})
    assert res_me.status_code == 200
    assert res_me.json()['role'] if 'role' in res_me.json() else 'user_name' in res_me.json()

