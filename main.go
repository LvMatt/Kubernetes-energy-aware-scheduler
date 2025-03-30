package main

import (
	"energy-scheduler/plugins" // Correct import path

	"k8s.io/klog/v2"
	app "k8s.io/kubernetes/cmd/kube-scheduler/app"
)

func main() {
	klog.Info("Starting Energy Efficient Scheduler Plugin...")
	defer klog.Flush()
	command := app.NewSchedulerCommand(
		app.WithPlugin(plugins.PluginName, plugins.New), // Register plugin
	)

	if err := command.Execute(); err != nil {
		klog.Fatal(err)
	}

	select {} // Keep running
}
