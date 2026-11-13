"""Add explicit audit categories without altering immutable original job statuses."""
def classify_status(original):
    state = dict(original)
    status, reason = state['status'], state.get('reason', '')
    if status == 'excluded':
        category = ('zero_usable_points' if state.get('occurrence_counts', {}).get('unique_cell') == 0
                    else 'insufficient_unique_cells')
    elif status == 'failed':
        category = ('no_aicc_eligible_model' if reason.startswith('no_AICc') else
                    'partition_failure' if reason.startswith('partition_failure') else
                    'container_failure' if reason.startswith('container_exit') else 'model_failure')
    else:
        category = status
    state['classification'] = category
    return state
