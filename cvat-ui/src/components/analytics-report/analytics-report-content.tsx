// Copyright (C) CVAT.ai Corporation
//
// SPDX-License-Identifier: MIT

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useSelector } from 'react-redux';

import config from 'config';
import { Project, Task, Job } from 'cvat-core-wrapper';
import { CombinedState } from 'reducers';
import PaidFeaturePlaceholder from 'components/paid-feature-placeholder/paid-feature-placeholder';
import { TimePeriod } from '.';
import Button from 'antd/lib/button';
import Select from 'antd/lib/select';
import Spin from 'antd/lib/spin';
import Alert from 'antd/lib/alert';
import Empty from 'antd/lib/empty';

interface Props {
    resource: Project | Task | Job;
    timePeriod: TimePeriod | null;
}

interface AnnotationCount {
    label_id: number;
    label_name: string;
    count: number;
}

interface AnnotationCountsResponse {
    counts: AnnotationCount[];
    total: number;
}

function AnnotationAnalytics({ task }: { task: Task }): JSX.Element {
    const [data, setData] = useState<AnnotationCountsResponse | null>(null);
    const [labelID, setLabelID] = useState<number | undefined>();
    const [error, setError] = useState<string | null>(null);
    const [fetching, setFetching] = useState(true);

    const loadCounts = useCallback(async () => {
        setFetching(true);
        setError(null);
        const query = labelID ? `?label_id=${labelID}` : '';

        try {
            const response = await fetch(`/api/test/tasks/${task.id}/annotation-counts${query}`, {
                credentials: 'same-origin',
            });
            if (!response.ok) {
                throw new Error(`The annotation counts request failed (${response.status})`);
            }
            setData(await response.json() as AnnotationCountsResponse);
        } catch (loadError: unknown) {
            setError(loadError instanceof Error ? loadError.message : 'Could not load annotation counts');
        } finally {
            setFetching(false);
        }
    }, [labelID, task.id]);

    useEffect(() => {
        loadCounts();
    }, [loadCounts]);

    const maximum = useMemo(
        () => Math.max(...(data?.counts.map((item) => item.count) || [0]), 1),
        [data],
    );

    if (fetching && !data) {
        return <Spin tip='Loading annotation counts' />;
    }

    if (error && !data) {
        return (
            <Alert
                type='error'
                message='Could not load annotation counts'
                description={error}
                action={<Button onClick={loadCounts}>Retry</Button>}
            />
        );
    }

    return (
        <section aria-labelledby='annotation-analytics-title'>
            <h2 id='annotation-analytics-title'>Annotation counts by label</h2>
            <Select
                allowClear
                placeholder='Filter by label'
                value={labelID}
                onChange={setLabelID}
                options={(data?.counts || []).map((item) => ({
                    value: item.label_id,
                    label: item.label_name,
                }))}
                style={{ minWidth: 220, marginBottom: 16 }}
            />
            {error && (
                <Alert
                    type='warning'
                    showIcon
                    message={error}
                    action={<Button onClick={loadCounts}>Retry</Button>}
                />
            )}
            {!data?.counts.length ? (
                <Empty description='No annotations found for this task' />
            ) : (
                <>
                    <div role='img' aria-label='Bar graph of annotation counts by label'>
                        {data.counts.map((item) => (
                            <div key={item.label_id} style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
                                <span style={{ width: 160 }}>{item.label_name}</span>
                                <div
                                    style={{
                                        height: 20,
                                        width: `${(item.count / maximum) * 100}%`,
                                        minWidth: 2,
                                        background: '#1677ff',
                                    }}
                                />
                                <span style={{ marginLeft: 8 }}>{item.count}</span>
                            </div>
                        ))}
                    </div>
                    <table>
                        <caption>Total annotations: {data.total}</caption>
                        <thead>
                            <tr><th scope='col'>Label</th><th scope='col'>Count</th></tr>
                        </thead>
                        <tbody>
                            {data.counts.map((item) => (
                                <tr key={item.label_id}>
                                    <th scope='row'>{item.label_name}</th>
                                    <td>{item.count}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </>
            )}
        </section>
    );
}

function AnalyticsReportContent({ resource }: Readonly<Props>): JSX.Element {
    if (resource instanceof Task) {
        return <AnnotationAnalytics task={resource} />;
    }

    return (
        <PaidFeaturePlaceholder featureDescription={config.PAID_PLACEHOLDER_CONFIG.features.analyticsReport} />
    );
}

function AnalyticsReportContentWrap(props: Readonly<Props>): JSX.Element {
    const overrides = useSelector(
        (state: CombinedState) => state.plugins.overridableComponents.analyticsReportPage.content,
    );

    if (overrides.length) {
        const [Component] = overrides.slice(-1);
        return <Component {...props} />;
    }

    return <AnalyticsReportContent />;
}

export default React.memo(AnalyticsReportContentWrap);
