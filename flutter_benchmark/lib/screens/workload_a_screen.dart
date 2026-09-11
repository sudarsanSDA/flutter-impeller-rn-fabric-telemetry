import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../models/list_item.dart';

/// Screen 1: Workload A executing virtualized list scrolling with 5,000 items.
class WorkloadAScreen extends StatefulWidget {
  /// Route path for [WorkloadAScreen].
  static const String routeName = '/workload_a';

  /// Creates a [WorkloadAScreen] instance.
  const WorkloadAScreen({super.key});

  @override
  State<WorkloadAScreen> createState() => _WorkloadAScreenState();
}

class _WorkloadAScreenState extends State<WorkloadAScreen> {
  List<ListItem> _items = const [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    final String rawJson = await rootBundle.loadString('assets/data/list_5k.json');
    final List<dynamic> parsed = jsonDecode(rawJson) as List<dynamic>;
    final List<ListItem> items = parsed
        .map((e) => ListItem.fromJson(e as Map<String, dynamic>))
        .toList();

    if (mounted) {
      setState(() {
        _items = items;
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Workload A: Virtualized List'),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
              key: const Key('virtualized_list_view'),
              itemCount: _items.length,
              itemExtent: 72.0,
              cacheExtent: 0.0,
              addAutomaticKeepAlives: false,
              itemBuilder: (BuildContext context, int index) {
                final ListItem item = _items[index];
                return _buildListItem(item);
              },
            ),
    );
  }

  Widget _buildListItem(ListItem item) {
    return Container(
      height: 72.0,
      padding: const EdgeInsets.symmetric(horizontal: 16.0),
      decoration: const BoxDecoration(
        border: Border(
          bottom: BorderSide(
            color: Color(0xFFEEEEEE),
            width: 1.0,
          ),
        ),
      ),
      child: Row(
        children: [
          ClipOval(
            child: Image.asset(
              'assets/images/avatar.png',
              width: 40.0,
              height: 40.0,
              fit: BoxFit.cover,
            ),
          ),
          const SizedBox(width: 12.0),
          Expanded(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  item.title,
                  style: const TextStyle(
                    fontSize: 16.0,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4.0),
                Text(
                  item.subtitle,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    fontSize: 14.0,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 12.0),
          Container(
            width: 24.0,
            height: 24.0,
            decoration: BoxDecoration(
              color: Colors.blueGrey.shade100,
              shape: BoxShape.circle,
            ),
            child: Center(
              child: Text(
                '${item.badgeCount}',
                style: const TextStyle(
                  fontSize: 11.0,
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
