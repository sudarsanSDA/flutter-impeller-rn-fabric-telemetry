/// Model representing an item in the virtualized list workload.
class ListItem {
  /// Unique identifier of the item.
  final int id;

  /// Primary display title.
  final String title;

  /// Secondary metadata description.
  final String subtitle;

  /// Numeric count displayed in trailing badge.
  final int badgeCount;

  /// Creates a [ListItem] instance.
  const ListItem({
    required this.id,
    required this.title,
    required this.subtitle,
    required this.badgeCount,
  });

  /// Deserializes a [ListItem] from a JSON map.
  factory ListItem.fromJson(Map<String, dynamic> json) {
    return ListItem(
      id: json['id'] as int,
      title: json['title'] as String,
      subtitle: json['subtitle'] as String,
      badgeCount: json['badge_count'] as int,
    );
  }
}
