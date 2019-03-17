#!/usr/bin/env python3
import abc


class FlowTracer(abc.ABCMeta):
    def __init__(self):
        self.flow_rule_hits = {}
        self.links_traversed = []

    @abc.abstractmethod
    def trace_flows(self, source, dest):
        pass